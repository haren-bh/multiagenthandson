from datetime import datetime
from google import genai
from google.genai import types
from google.adk.tools import ToolContext
from google.cloud import storage
from .... import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


client = genai.Client(
    vertexai=True
)

async def generate_images(imagen_prompt: str, tool_context: ToolContext):
    try:
        MODEL_ID = config.IMAGEN_MODEL

        logging.error(MODEL_ID)
        
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=imagen_prompt,
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
            ),
        )

        # Check for errors if an image is not generated
# Check for errors if an image is not generated
        if response.candidates[0].finish_reason != types.FinishReason.STOP:
            reason = response.candidates[0].finish_reason
            raise ValueError(f"Prompt Content Error: {reason}")
            
        image_bytes = None
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.thought:
                    continue
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    break

        if image_bytes is not None:
            counter = str(tool_context.state.get("loop_iteration", 0))
            artifact_name = f"generated_image_" + counter + ".png"
            
            # call save to gcs function
            if config.GCS_BUCKET_NAME:
                logger.info(f"DEBUG: GCS_BUCKET_NAME is set to {config.GCS_BUCKET_NAME}. Calling save_to_gcs...")
                save_to_gcs(tool_context, image_bytes, artifact_name, counter)
            else:
                logger.info("DEBUG: GCS_BUCKET_NAME is NOT set. Skipping save_to_gcs.")

            # Save as ADK artifact (optional, if still needed by other ADK components)
            report_artifact = types.Part.from_bytes(
                data=image_bytes, mime_type="image/png"
            )

            await tool_context.save_artifact(artifact_name, report_artifact)
            logger.info(f"Image also saved as ADK artifact: {artifact_name}")

            return {
                "status": "success",
                "message": f"Image generated .  ADK artifact: {artifact_name}.",
                "artifact_name": artifact_name,
            }
        else:
            # model_dump_json might not exist or be the best way to get error details
            error_details = str(response)  # Or a more specific error field if available
            logger.error(f"No images generated. Response: {error_details}")
            return {
                "status": "error",
                "message": f"No images generated. Response: {error_details}",
            }                    
    except Exception as e:
        # Keep your existing error handling here...
        logger.exception(f"Error generating images: {e}")
        logger.error(f"Error generating images: {e}")
        return {"status": "error", "message": f"No images generated.  {e}"}

"""
async def generate_images_old(imagen_prompt: str, tool_context: ToolContext):

    try:

        response = client.models.generate_images(
            model=config.IMAGEN_MODEL,
            prompt=imagen_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="9:16",
                safety_filter_level="block_low_and_above",
                person_generation="allow_adult",
            ),
        )
        generated_image_paths = []
        if response.generated_images is not None:
            for generated_image in response.generated_images:
                # Get the image bytes
                image_bytes = generated_image.image.image_bytes
                counter = str(tool_context.state.get("loop_iteration", 0))
                artifact_name = f"generated_image_" + counter + ".png"
                # call save to gcs function
                if config.GCS_BUCKET_NAME:
                    logger.info(f"DEBUG: GCS_BUCKET_NAME is set to {config.GCS_BUCKET_NAME}. Calling save_to_gcs...")
                    save_to_gcs(tool_context, image_bytes, artifact_name, counter)
                else:
                    logger.info("DEBUG: GCS_BUCKET_NAME is NOT set. Skipping save_to_gcs.")

                # Save as ADK artifact (optional, if still needed by other ADK components)
                report_artifact = types.Part.from_bytes(
                    data=image_bytes, mime_type="image/png"
                )

                await tool_context.save_artifact(artifact_name, report_artifact)
                logger.info(f"Image also saved as ADK artifact: {artifact_name}")

                return {
                    "status": "success",
                    "message": f"Image generated .  ADK artifact: {artifact_name}.",
                    "artifact_name": artifact_name,
                }
        else:
            # model_dump_json might not exist or be the best way to get error details
            error_details = str(response)  # Or a more specific error field if available
            logger.error(f"No images generated. Response: {error_details}")
            return {
                "status": "error",
                "message": f"No images generated. Response: {error_details}",
            }

    except Exception as e:
        logger.error(f"Error generating images: {e}")
        return {"status": "error", "message": f"No images generated.  {e}"}
"""


def save_to_gcs(tool_context: ToolContext, image_bytes, filename: str, counter: str):
    # --- Save to GCS ---
    storage_client = storage.Client()  # Initialize GCS client
    bucket_name = config.GCS_BUCKET_NAME

    unique_id = tool_context.state.get("unique_id", "")
    current_date_str = datetime.utcnow().strftime("%Y-%m-%d")
    unique_filename = filename
    gcs_blob_name = f"{current_date_str}/{unique_id}/{unique_filename}"

    logger.info(f"DEBUG: Starting save_to_gcs with bucket: {bucket_name}")
    logger.info(f"DEBUG: Target blob name: {gcs_blob_name}")

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(gcs_blob_name)

    try:
        blob.upload_from_string(image_bytes, content_type="image/png")
        gcs_uri = f"gs://{bucket_name}/{gcs_blob_name}"
        logger.info(f"DEBUG: Successfully uploaded to GCS: {gcs_uri}")

        # Store GCS URI in session context
        # Store GCS URI in session context
        tool_context.state["generated_image_gcs_uri_" + counter] = gcs_uri

    except Exception as e_gcs:
        logger.error(f"DEBUG: Error uploading to GCS: {e_gcs}")
        # Decide if this is a fatal error for the tool
        return {
            "status": "error",
            "message": f"Image generated but failed to upload to GCS: {e_gcs}",
        }
        # --- End Save to GCS ---
