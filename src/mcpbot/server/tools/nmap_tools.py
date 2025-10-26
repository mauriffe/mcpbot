from mcp import types
from fastmcp import Context
import logging
import nmap

logger = logging.getLogger(__name__)

def register_nmap_tools(mcp):
    @mcp.tool(
        name="scan_specific_port",
        description="Scan the specified port of the specified target.",  # Custom description
        tags={"sensitive", "nmap"},  # Optional tags for organization/filtering
        meta={"version": "1.2", "author": "support-team"},  # Custom metadata
        annotations=types.ToolAnnotations(
            title="Nmap scan specific port",
            readOnlyHint=True,  # If true, the tool does not modify its environment.
            destructiveHint=False,  # If true, the tool may perform destructive updates to its environment.
            idempotentHint=True,
            # If true, calling the tool repeatedly with the same arguments will have no additional effect on the environment.
            openWorldHint=False,
            # If true, this tool may interact with an “open world” of external entities. If false, the tool’s domain of interaction is closed.
        )
    )
    def scan_specific_port(target: str, port: str, timeout: int = 30) -> dict:
        """
        Nmap scan specific port

        Args:
            target (str): The target domain to scan.
            port (str): the port to scan.
            timeout (int, optional): The timeout to use. Defaults to 30.

        Returns:
            dict: The port scan results in json format.
        """
        logger.info(f"Executing Nmap scan on {target}  port {port} ")
        try:
            nm = nmap.PortScanner()
            response = nm.scan(target, port, arguments=f'-sV -Pn --host-timeout={timeout}')
            logger.info(response['scan'])
            output = response['scan']
            return output
        except Exception as e:
            logger.exception("Nmap scan scan_specific_port failed")
            return {"result": f"Nmap scan on {target}  port {port} failed with error {e}"}

    @mcp.tool(
        name="ssl_enum_cipher",
        description="Scan the specified port of the specified target to know the SSL/TLS protocol offered as well as the cipher offered",  # Custom description
        tags={"sensitive", "nmap"},  # Optional tags for organization/filtering
        meta={"version": "1.2", "author": "support-team"},  # Custom metadata
        annotations=types.ToolAnnotations(
            title="Nmap scan specific port for ssl cipher and protocol enumeration",
            readOnlyHint=True,  # If true, the tool does not modify its environment.
            destructiveHint=False,  # If true, the tool may perform destructive updates to its environment.
            idempotentHint=True,
            # If true, calling the tool repeatedly with the same arguments will have no additional effect on the environment.
            openWorldHint=False,
            # If true, this tool may interact with an “open world” of external entities. If false, the tool’s domain of interaction is closed.
        )
    )
    def ssl_enum_cipher(target: str, port: str, timeout: int = 30) -> dict:
        """
        Scan the specified port of the specified target to know the SSL/TLS protocol offered as well as the cipher offered

        Args:
            target (str): The target domain to scan.
            port (str): the port to scan.
            timeout (int, optional): The timeout to use. Defaults to 30.

        Returns:
            dict: The port scan results in json format.
        """
        logger.info(f"Executing Nmap scan ssl_enum_cipher on {target}  port {port} ")
        try:
            nm = nmap.PortScanner()
            response = nm.scan(target, port, arguments=f'-sV -Pn --script=ssl-enum-ciphers --host-timeout={timeout}')
            # Read the output and convert to list
            logger.info(response['scan'])
            output = response['scan']
            return output
        except Exception as e:
            logger.exception("Nmap scan ssl_enum_cipher failed")
            return {"result": f"Nmap scan on {target}  port {port} failed with error {e}"}