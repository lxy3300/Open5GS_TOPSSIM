#!/usr/bin/env python3

import subprocess
import json
import sys

SUPI = "imsi-999700000000002"

H_AMF_URL = "http://127.0.1.5:7777"
V_AMF_URL = "http://127.0.0.5:7777"
V_SCP_URL = "http://127.0.0.200:7777"

V_SMF_TARGET = "http://smf.5gc.mnc001.mcc001.3gppnetwork.org"
V_AMF_CALLBACK = f"http://127.0.0.5:7777/namf-callback/v1/{SUPI}/sm-context-status"


def curl_post(url, body, headers=None):
    cmd = [
        "curl", "-s", "-w", "\n%{http_code}",
        "--http2-prior-knowledge",
        "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-d", json.dumps(body),
    ]

    print(cmd)
    if headers:
        for h in headers:
            cmd += ["-H", h]

    result = subprocess.run(cmd, capture_output=True, text=True)
    raw = result.stdout.strip()

    lines = raw.rsplit("\n", 1)
    status = int(lines[-1]) if lines[-1].isdigit() else 0

    body_str = lines[0] if len(lines) > 1 else ""
    try:
        data = json.loads(body_str) if body_str else {}
    except Exception:
        data = {}

    return status, data


def get_ue_context_from_H_PLMN():
    url = f"{H_AMF_URL}/namf-comm/v1/ue-contexts/{SUPI}/transfer"
    body = {"reason": "MOBI_REG", "accessType": "3GPP_ACCESS"}

    status, resp = curl_post(url, body)
    if status != 200:
        sys.exit("Step1 failed")

    ue_context = resp.get("ueContext")
    if not ue_context:
        sys.exit("No ueContext returned")

    sessions = ue_context.get("sessionContextList", [])

    if sessions:
        s = sessions[0]
        psi = s.get("pduSessionId", 1)
        dnn = s.get("dnn", "internet")
        s_nssai = s.get("sNssai", {"sst": 1})
    else:
        psi, dnn, s_nssai = 1, "internet", {"sst": 1}

    return ue_context, psi, dnn, s_nssai


def push_UE_to_v_amf(ue_context):
    url = f"{V_AMF_URL}/nsco-handover/v1/ue-contexts/{SUPI}/prepare"
    status, _ = curl_post(url, {"ueContext": ue_context})

    if status not in (200, 204):
        sys.exit("Step2 failed")


def create_sm_context(psi, dnn, s_nssai):
    url = f"{V_SCP_URL}/nsco-nsmf-pdusession/v1/handover-sm-contexts"

    body = {
        "supi": SUPI,
        "pduSessionId": psi,
        "dnn": dnn,
        "sNssai": s_nssai,
        "servingNfId": "nsco-amf-id",
        "servingNetwork": {"mcc": "001", "mnc": "01"},
        "requestType": "EXISTING_PDU_SESSION",
        "anType": "3GPP_ACCESS",
        "smContextStatusUri": V_AMF_CALLBACK,
    }

    headers = [
        "User-Agent: AMF",
        f"3gpp-Sbi-Target-apiRoot: {V_SMF_TARGET}",
    ]

    status, _ = curl_post(url, body, headers)

    if status not in (200, 201, 204):
        sys.exit("Step3 failed")


def main():
    ue_context, psi, dnn, s_nssai = get_ue_context_from_H_PLMN()
    push_UE_to_v_amf(ue_context)
    create_sm_context(psi, dnn, s_nssai)


if __name__ == "__main__":
    main()