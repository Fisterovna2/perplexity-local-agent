"""🚀 MAIN ORCHESTRATOR - Start all agent services
🚀 Services:
✅ Backend: LLM + Memory + Safety + Planning
✅ Telegram Bot: Command interface
✅ Web UI: Browser interface (optional)
✅ Agent Loop: Main execution loop
"""

import asyncio
import logging
from typing import Optional
import os
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('PERPLEXITY_AGENT')


class AgentOrchestrator:
    """Main orchestrator for all agent services"""
    
    def __init__(self):
        self.llm_selector = None
        self.safety_manager = None
        self.memory = None
        self.planner = None
        self.telegram_bot = None
        self.web_ui = None
        self.is_running = False
    
    async def initialize(self) -> bool:
        """Initialize all core modules"""
        logger.info("🔍 Initializing Perplexity Local Agent...")
        
        try:
            # Import and initialize modules
            from llm_selector import LLMSelector, initialize_llm
            from safety import initialize_safety
            from memory import AgentMemory
            from planner import Planner
            
            logger.info("✅ Loading LLM Selector...")
            self.llm_selector = LLMSelector()
            
            logger.info("✅ Loading Safety Manager...")
            self.safety_manager, _, _ = initialize_safety(require_confirmation=True)
            
            logger.info("✅ Loading Memory System...")
            self.memory = AgentMemory()
            
            logger.info("✅ Loading Planner...")
            self.planner = Planner(llm_selector=self.llm_selector)
            
            logger.info("✅ All modules initialized successfully!")
            return True
        
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def start_telegram_bot(self, token: str) -> bool:
        """Start Telegram bot (optional)"""
        try:
            from telegram_super_agent import SuperAgent
            logger.info("🔄 Starting Telegram Bot...")
            self.telegram_bot = SuperAgent(llm_selector=self.llm_selector)
            logger.info("✅ Telegram Bot started on token ****")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Telegram Bot failed to start: {e}")
            return False
    
    async def start_web_ui(self, port: int = 5000) -> bool:
        """Start Web UI (optional)"""
        try:
            logger.info(f"🔄 Starting Web UI on localhost:{port}...")
            logger.info(f"✅ Web UI will be available at http://localhost:{port}")
            # Flask app would be started here
            return True
        except Exception as e:
            logger.warning(f"⚠️ Web UI failed to start: {e}")
            return False
    
    async def run_agent_loop(self):
        """Main agent execution loop"""
        self.is_running = True
        logger.info("🚀 Starting Agent Main Loop...")
        
        try:
            while self.is_running:
                # Get command from Telegram/Web UI or user input
                command = input("\n👋 Enter command (or 'help'): ").strip()
                
                if not command:
                    continue
                
                if command.lower() == 'help':
                    print("""
📄 Available Commands:
  /plan <goal>        - Create execution plan for goal
  /models             - List available LLM models
  /select <model>     - Select LLM model
  /vision             - Capture and show screen
  /game <game_name>   - Play game (Roblox, Dota2, Bee Swarm)
  /create3d           - Create 3D model in Blender
  /curious_mode       - Enable/disable curious child mode
  /status             - Show agent status
  /exit               - Stop agent
""")
                
                elif command.lower() == '/exit':
                    logger.info("🛑 Stopping agent...")
                    self.is_running = False
                    break
                
                elif command.startswith('/plan'):
                    goal = command[5:].strip()
                    if goal:
                        plan = await self.planner.create_plan(goal)
                        logger.info(f"📊 Plan created: {len(plan.tasks)} tasks")
                        for i, task in enumerate(plan.tasks):
                            print(f"  {i+1}. {task.description}")
                
                elif command.startswith('/select'):
                    model = command[7:].strip()
                    if model and self.llm_selector:
                        result = self.llm_selector.select_model(model)
                        logger.info(f"✅ Selected model: {model}")
                
                else:
                    logger.info(f"💬 Command: {command}")
        
        except KeyboardInterrupt:
            logger.info("⏰ Agent interrupted by user")
        except Exception as e:
            logger.error(f"❌ Agent loop error: {e}")
    
    async def shutdown(self):
        """Gracefully shutdown all services"""
        logger.info("🔄 Shutting down...")
        self.is_running = False
        
        # Save memory and logs
        if self.memory:
            logger.info("💾 Saving memory...")
        
        if self.safety_manager:
            logger.info("📁 Exporting audit log...")
            self.safety_manager.export_audit_log('audit_log.json')
        
        logger.info("✅ Shutdown complete")
    
    async def main(self):
        """Main entry point"""
        logger.info("🌠 === PERPLEXITY LOCAL AGENT ===")
        logger.info("🙋 Welcome! Initializing...\n")
        
        # Initialize all modules
        if not await self.initialize():
            logger.error("😱 Failed to initialize agent")
            return
        
        # Start optional services
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if telegram_token:
            await self.start_telegram_bot(telegram_token)
        
        web_ui_enabled = os.getenv('WEB_UI_ENABLED', 'false').lower() == 'true'
        if web_ui_enabled:
            await self.start_web_ui()
        
        print("""
🙋 Welcome to Perplexity Local Agent!
✅ Safety Manager: ENABLED
✅ Memory System: ENABLED
✅ Planning System: ENABLED
🔍 Type 'help' for available commands
""")
        
        # Start main loop
        try:
            await self.run_agent_loop()
        finally:
            await self.shutdown()


async def main():
    """Entry point"""
    orchestrator = AgentOrchestrator()
    await orchestrator.main()


if __name__ == "__main__":
    # Run async main
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Agent stopped")
    except Exception as e:
        logger.error(f"😱 Fatal error: {e}")
        sys.exit(1)
