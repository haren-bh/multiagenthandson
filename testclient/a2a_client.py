import httpx
import uuid
from typing import Any, Dict, List, Optional, Union

class JsonRpcError(Exception):
    """Custom exception for JSON-RPC errors."""
    def __init__(self, code: int, message: str, data: Optional[Any] = None, request_id: Optional[Union[str, int]] = None):
        super().__init__(f"JSON-RPC Error {code}: {message}")
        self.code = code
        self.message = message
        self.data = data
        self.request_id = request_id

class JsonRpcClient:
    """
    A client for making JSON-RPC 2.0 calls to a server.
    """
    def __init__(self, server_url: str, httpx_client: Optional[httpx.AsyncClient] = None):
        """
        Initializes the JSON-RPC client.

        Args:
            server_url: The URL of the JSON-RPC server.
            httpx_client: An optional existing httpx.AsyncClient instance.
                          If None, a new one will be created and managed internally
                          for each call (less efficient for multiple calls).
        """
        self.server_url = server_url
        self._httpx_client = httpx_client
        self._owns_client = httpx_client is None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._httpx_client:
            return self._httpx_client
        return httpx.AsyncClient()

    async def close(self):
        """
        Closes the underlying httpx.AsyncClient if it was created by this instance.
        """
        if self._httpx_client and self._owns_client:
            await self._httpx_client.aclose()
            self._httpx_client = None

    async def __aenter__(self):
        if self._owns_client and self._httpx_client is None:
            self._httpx_client = httpx.AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def call(
        self,
        method: str,
        params: Optional[Union[Dict[str, Any], List[Any]]] = None,
        request_id: Optional[Union[str, int]] = None
    ) -> Any:
        """
        Makes a JSON-RPC 2.0 call to the server.

        Args:
            method: The name of the method to call.
            params: The parameters for the method, can be a dict or a list.
            request_id: An optional unique identifier for the request.
                        If None, a UUID will be generated.

        Returns:
            The 'result' field from the JSON-RPC response.

        Raises:
            httpx.HTTPStatusError: If the server returns an HTTP error status.
            JsonRpcError: If the JSON-RPC response contains an error.
            ValueError: If the response is not valid JSON or not a JSON-RPC response.
        """
        if request_id is None:
            request_id = str(uuid.uuid4())

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": request_id
        }
        if params is not None:
            payload["params"] = params

        client = await self._get_client()

        try:
            response = await client.post(
                self.server_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()  # Raise an exception for HTTP 4xx/5xx errors
        except httpx.HTTPStatusError as e:
            # You might want to log e.response.text for more details
            raise httpx.HTTPStatusError(
                f"HTTP error calling {method}: {e.response.status_code} - {e.response.text}",
                request=e.request,
                response=e.response
            )
        except httpx.RequestError as e:
            # Handle network errors, timeouts, etc.
            raise httpx.RequestError(
                f"Request error calling {method}: {e}",
                request=e.request
            )
        finally:
            if self._owns_client and client: # if client was created in _get_client
                await client.aclose()


        try:
            response_data = response.json()
        except ValueError:
            raise ValueError(f"Invalid JSON response from server: {response.text}")

        if "error" in response_data and response_data["error"] is not None:
            error_info = response_data["error"]
            raise JsonRpcError(
                code=error_info.get("code"),
                message=error_info.get("message"),
                data=error_info.get("data"),
                request_id=response_data.get("id")
            )

        if "result" not in response_data:
            raise ValueError(f"Invalid JSON-RPC response: 'result' field missing. Response: {response_data}")

        if response_data.get("id") != request_id:
            # This check is important for matching responses to requests,
            # though less critical if you await every call.
            # For notifications (id=null), this check would be different.
            print(f"Warning: Response ID '{response_data.get('id')}' does not match request ID '{request_id}'.")


        return response_data["result"]

    async def notify(
        self,
        method: str,
        params: Optional[Union[Dict[str, Any], List[Any]]] = None
    ) -> None:
        """
        Sends a JSON-RPC 2.0 notification to the server.
        Notifications do not have an 'id' and do not expect a response body.

        Args:
            method: The name of the method to call.
            params: The parameters for the method, can be a dict or a list.

        Raises:
            httpx.HTTPStatusError: If the server returns an HTTP error status.
            httpx.RequestError: For network errors.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
        }
        if params is not None:
            payload["params"] = params

        client = await self._get_client()
        try:
            response = await client.post(
                self.server_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            # For notifications, a 204 No Content is common, or 200 OK with empty body.
            # Some servers might return 202 Accepted.
            # We'll raise for 4xx/5xx client/server errors.
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise httpx.HTTPStatusError(
                f"HTTP error sending notification {method}: {e.response.status_code} - {e.response.text}",
                request=e.request,
                response=e.response
            )
        except httpx.RequestError as e:
            raise httpx.RequestError(
                f"Request error sending notification {method}: {e}",
                request=e.request
            )
        finally:
            if self._owns_client and client:
                await client.aclose()

# Example Usage:
async def example_main():
    # This is a placeholder URL. Replace with your actual JSON-RPC server URL.
    # For instance, if you are running the server from the context locally:
    # server_url = "http://localhost:10002/jsonrpc"
    # Note: The provided server context seems to use a base URL for agent card
    # and then specific paths for JSON-RPC might be implied by the A2AClient.
    # For a generic JSON-RPC server, you'd point to its direct RPC endpoint.
    # The A2AServer in context might not expose a generic /jsonrpc endpoint
    # directly without further configuration or a different design.
    # This example assumes a standard JSON-RPC endpoint.

    server_url = "http://localhost:10002" # Adjust if your server has a specific /jsonrpc path

    # Option 1: Client manages its own httpx.AsyncClient per call (less efficient for many calls)
    # client = JsonRpcClient(server_url=server_url)

    # Option 2: Share an httpx.AsyncClient (more efficient for many calls)
    async with httpx.AsyncClient() as httpx_client:
        # The client from the context uses the agent card URL to discover the actual RPC endpoint.
        # For this generic client, we assume `server_url` is the direct RPC endpoint.
        # If your server from the context (MyAgentTaskManager) is at http://localhost:10002
        # and it directly handles JSON-RPC at the root, this URL is fine.
        # The A2A protocol might have specific method names like "టం/sendTask".

        # Let's try to call the `టం/sendTask` method from your MyAgentTaskManager
        # This assumes the A2AServer routes `/` or a specific path to the task manager's JSON-RPC methods.
        # The actual method name for `on_send_task` via JSON-RPC would be "టం/sendTask"
        # as per A2A specification (టం is the namespace for tasks).

        client = JsonRpcClient(server_url=server_url, httpx_client=httpx_client)

        try:
            # Example of calling a method that might exist on your A2A server
            # This payload structure is based on `SendTaskRequest` from your context
            task_params = {
                "id": str(uuid.uuid4()),
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": "Hello from JsonRpcClient!"}],
                    "messageId": str(uuid.uuid4())
                }
                # Add other fields like 'skillInvocation' if required by your server's SendTaskRequest
            }
            print(f"Calling 'tasks/send' with params: {task_params}")
            # The method name for on_send_task is typically "టం/sendTask" in A2A
            response_result = await client.call(method="tasks/send", params=task_params)
            print("\nResponse from 'టం/sendTask':")
            print(response_result)

        except JsonRpcError as e:
            print(f"\nJSON-RPC Error: {e.code} - {e.message}")
            if e.data:
                print(f"Error Data: {e.data}")
        except httpx.HTTPStatusError as e:
            print(f"\nHTTP Error: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        except httpx.RequestError as e:
            print(f"\nRequest Error: {e}")
        except ValueError as e:
            print(f"\nValue Error / Invalid Response: {e}")

if __name__ == "__main__":
    import asyncio
    # To run this example, you need a JSON-RPC server running at the specified URL.
    # If you run the a2aagents server from your context, it will be at http://localhost:10002
    # and should respond to A2A specific methods like "టం/sendTask" or "టం/getAgentCard".
    print("Attempting to connect to a JSON-RPC server.")
    print("Ensure your a2aagents server (or another JSON-RPC server) is running.")
    asyncio.run(example_main())
