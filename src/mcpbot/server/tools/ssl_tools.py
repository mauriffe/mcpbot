from mcp import types
from fastmcp import Context
import logging
import socket
import ssl

logger = logging.getLogger(__name__)

def register_ssl_tools(mcp):
    @mcp.tool(
        name="get_ssl_cert",
        description="Retrieves the SSL certificate information in dictionary form the specified port of the specified target, supporting custom SNI.",  # Custom description
        tags={"sensitive", "ssl", "certificate"},  # Optional tags for organization/filtering
        meta={"version": "1.2", "author": "support-team"},  # Custom metadata
        annotations=types.ToolAnnotations(
            title="Get SSL certificate details",
            readOnlyHint=True,  # If true, the tool does not modify its environment.
            destructiveHint=False,  # If true, the tool may perform destructive updates to its environment.
            idempotentHint=True,
            # If true, calling the tool repeatedly with the same arguments will have no additional effect on the environment.
            openWorldHint=False,
            # If true, this tool may interact with an “open world” of external entities. If false, the tool’s domain of interaction is closed.
        )
    )
    def get_cert_simple(host: str, port: int = 443, timeout: int = 30,sni_name: str | None = None) -> dict:
        """
        Retrieve the SSL/TLS certificate from a remote endpoint, supporting custom SNI.

        Args:
            host (str): The hostname or IP address of the target server.
            port (int, optional): The TCP port to connect to. Defaults to 443.
            timeout (int, optional): Connection timeout in seconds. Defaults to 5.
            sni_name (str | None, optional): Hostname to use for SNI.
                If None, uses `host`. Set to "" to disable SNI.

        Returns:
            dict: On success, returns parsed certificate fields.
                  On failure, returns {"error": "<message>"}.
        """
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=timeout) as sock:
                # If sni_name is an empty string, disable SNI
                sni_hostname = None if sni_name == "" else (sni_name or host)
                with ctx.wrap_socket(sock, server_hostname=sni_hostname) as ssock:
                    cert = ssock.getpeercert()
            return cert

        except socket.timeout:
            return {"error": f"Connection to {host}:{port} timed out after {timeout}s"}
        except ssl.SSLError as e:
            return {"error": f"SSL error when connecting to {host}:{port}: {e}"}
        except ConnectionRefusedError:
            return {"error": f"Connection refused by {host}:{port}"}
        except socket.gaierror:
            return {"error": f"DNS resolution failed for host: {host}"}
        except Exception as e:
            return {"error": f"Unexpected error connecting to {host}:{port}: {e}"}