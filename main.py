from app import create_app
import uvicorn


if __name__ == '__main__':
    uvicorn.run("main:create_app", host="0.0.0.0", port=4002, factory=True)
