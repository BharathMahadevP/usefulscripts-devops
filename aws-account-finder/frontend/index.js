function isValidIPOrEC2InstanceID(input) {
  const ipRegex =
    /^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}$/;
  const ec2InstanceIdRegex = /^i-[0-9a-f]{17}$/;

  if (ipRegex.test(input)) {
    const inputType = "ip";
    return inputType;
  } else if (ec2InstanceIdRegex.test(input)) {
    const inputType = "ec2";
    return inputType;
  } else {
    const inputType = "Invalid input";
    return inputType;
  }
}

async function searchInstance() {
  const searchdata = document.getElementById("data").value;
  if (!searchdata) {
    alert("Please enter an IP address or EC2 Instance ID");
    return;
  }
  // Validate the input
  const inputType = isValidIPOrEC2InstanceID(searchdata);
  if (inputType === "Invalid input") {
    alert(
      "Invalid input!!!\nPlease enter a valid IP address or EC2 Instance ID."
    );
    return;
  }
  const btn = document.querySelector("button");
  const resultDiv = document.getElementById("result");
  const resultDivTable = resultDiv.innerHTML;

  resultDiv.style.display = "block";
  resultDiv.innerHTML = "Fetching details...";

  try {
    btn.disabled = true;
    const res = await fetch(
      "https://aws-server-finder-backend.cloudops.qburst.build:443/find-instance",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ data: searchdata, inputType: inputType }),
      }
    );

    const data = await res.json();

    if (res.ok) {
      if (data.aws_account_id == "851874770356") {
        accountName = "Secondary AWS Account";
      } else if (data.aws_account_id == "150855778176") {
        accountName = "Primary AWS Account";
      }
      resultDiv.innerHTML = resultDivTable;
      document.getElementById("accountName").textContent = accountName;
      document.getElementById("label").textContent = data.label;
      document.getElementById("instance_id").textContent = data.instance_id;
      document.getElementById("region").textContent = data.region;
      document.getElementById("aws_account_id").textContent =
        data.aws_account_id;
      document.getElementById("pub_ip").textContent = data.public_ip;
      document.getElementById("pvt_ip").textContent = data.private_ip;
    } else {
      resultDiv.innerHTML = `<p class="error">❌ Instance not found in QBurst AWS Accounts</p>`;
    }
  } catch (err) {
    console.log(err);
    resultDiv.innerHTML = `<p class="error"> Error while fetching data: ${err.message}</p>`;
  } finally {
    btn.disabled = false;
  }
}
