from api import app
import uvicorn
import config
config.parse_args()


if __name__ == "__main__":
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=9000,
        log_level="info",
        reload=True)

    # Run the second app on port 9001
    # uvicorn.run(app2, host="0.0.0.0", port=9001, log_level="info")
