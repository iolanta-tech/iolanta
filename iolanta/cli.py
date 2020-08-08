import uvicorn


def serve():
    uvicorn.run(
        'iolanta.app:app',
        reload=True,
        port=8000,
    )
