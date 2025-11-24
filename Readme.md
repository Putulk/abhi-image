## To run script inside the pod

### 1. kubectl get po
    To check the pod
### 2. To Check file inside the pod
    kubectl exec -it <pod-name> -- head -n 5 /tmp/<filename>
### 3. To keep file inside the pod
    kubectl cp <filename with local path> <pod-name>:<file-name>
### 4. Go inside the pod
    kubectl exec -it <pod-name> -n prod -- /bin/bash
    
###    If bash not available
    kubectl exec -it <pod-name> -n prod -- /bin/sh
### 5. To install any requirements inside pod
    kubectl exec -it <pod-name> -- /tmp/pip install requests

    apk add --no-cache py3-requests
    apt-get update && apt-get install -y python3 python3-requests
    apk add --no-cache python3 py3-pip
    apt-get update && apt-get install -y python3 python3-pip
    apk add --no-cache py3-pycryptodome
    apt-get update && apt-get install -y python3 python3-pycryptodome
### 6. To check the file inside any folder on pod
    kubectl exec -it <pod-name> -- ls -lh /tmp
### 7. To run python script inside the pod
    kubectl exec -it <pod-name> -- /tmp/venv/bin/python /tmp/send_encrypted_payloads.py /tmp/whilterPB_2910_cleaned.csv

    python3  /tmp/send_encrypted_payloads_img.py /tmp/abhi_img.csv
###    for this add the python script to the pod also like csv file