import asyncio
from data_streaming import alpaca_stream
from strategies.composite_strategy import CompositeStrategy
from execution.order_manager import OrderManager

SYMBOL = "AAPL"
strategy = CompositeStrategy(SYMBOL)
order_manager = OrderManager(SYMBOL)

# Global variable to track if the processor is initialized
processor_initialized = False

async def live_trading_loop():
    global processor_initialized
    while True:
        try:
            if processor_initialized and 'processor' in globals() and not processor.processed_data.empty:
                latest_data = processor.processed_data.iloc[-1:]
                signal = strategy.generate_signal(latest_data)
                if signal in ["buy", "sell"]:
                    order_manager.place_bracket_order(signal)
            else:
                print("Waiting for processor to initialize...")
        except Exception as e:
            print(f"Error in trading loop: {e}")
        await asyncio.sleep(5)

async def main():
    global processor, processor_initialized
    processor = None
    processor_initialized = False

    # Start the stream in a separate task
    stream_task = asyncio.create_task(alpaca_stream.start_stream())

    # Wait for the processor to be initialized
    while True:
        if 'processor' in globals() and processor is not None:
            processor_initialized = True
            print("Processor initialized. Starting trading loop...")
            break
        await asyncio.sleep(1)

    # Run both tasks concurrently
    await asyncio.gather(stream_task, live_trading_loop())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
    except Exception as e:
        print(f"Fatal error: {e}")