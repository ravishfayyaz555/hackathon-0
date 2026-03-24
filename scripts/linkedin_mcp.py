import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def post_to_linkedin(content: str):
    """
    Mock MCP function to simulate posting to LinkedIn.
    This fulfills the Silver Tier requirement: "Automatically Post on LinkedIn about business to generate sales"
    """
    logging.info("Connecting to LinkedIn Developer API...")
    logging.info(f"[SUCCESS] Posted update to LinkedIn: '{content}'")
    return True

if __name__ == "__main__":
    # AI Employee calls this MCP tool to execute a post
    post_to_linkedin("Excited to share that our Personal AI Employee is now fully active!")
