from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from main import find_details
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://servers.cloudops.qburst.build",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IPRequest(BaseModel):
    data: str
    inputType: str


@app.post("/find-instance")
def find_instance(request: IPRequest): #: IPRequest
    result = find_details(request)
    # is_private_ip(request.ip)
    if result:
        instance_id, region, awsAccountId, label, public_ip, private_ip= result
        return {
            "instance_id": instance_id,
            "region": region,
            "aws_account_id": awsAccountId,
            "label": label,
            "public_ip": public_ip,
            "private_ip": private_ip
        }
    raise HTTPException(status_code=404, detail="Instance not found")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)
