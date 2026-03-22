#!/usr/bin/env python3
import asyncio
import re
import sys

import httpx


async def main(server_url: str = "http://localhost:3000"):
    base_url = server_url
    session_id = None

    print(f"1️⃣  Connecting to SSE stream at {base_url}...")
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            # Ouvrir le flux SSE pour obtenir le session_id
            async with client.stream('GET', f"{base_url}/sse") as response:
                print(f"SSE Status: {response.status_code}")

                # Lire les premières lignes du stream
                line_count = 0
                async for line in response.aiter_lines():
                    line_count += 1
                    print(f"  > {line}")

                    # Trouver le session_id dans la réponse
                    if "session_id=" in line:
                        match = re.search(r"session_id=([a-f0-9-]+)", line)
                        if match:
                            session_id = match.group(1)
                            print(f"✅ Got session_id: {session_id}")
                            break

                    if line_count > 5:
                        break

        except Exception as e:
            print(f"❌ Error reading SSE: {e}")
            import traceback
            traceback.print_exc()
            return

        if not session_id:
            print("❌ Could not extract session_id from SSE")
            return

        # Maintenant utiliser le session_id valid pour POST
        print(f"\n2️⃣  Sending initialize message with session_id={session_id}...")

        try:
            init_msg = {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0"},
                },
            }

            response = await client.post(
                f"{base_url}/messages/?session_id={session_id}",
                json=init_msg,
                timeout=60,
            )
            print(f"Response Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")

            if response.status_code == 202:
                print("✅ Initialize message accepted!")
            else:
                print(f"❌ Unexpected status: {response.status_code}")

        except Exception as e:
            print(f"❌ Error sending message: {e}")


if __name__ == "__main__":
    server_param = "localhost:3000"
    if len(sys.argv) > 1:
        server_param = sys.argv[1]
    
    # Parser le format server:port
    if ":" in server_param:
        server, port = server_param.rsplit(":", 1)
        url = f"http://{server}:{port}"
    else:
        # Si seulement le serveur est fourni, utiliser le port par défaut
        url = f"http://{server_param}:3000"
    
    print(f"Testing MCP server at {url}\n")
    asyncio.run(main(url))
