$aws_access_key_id = Read-Host -Prompt 'AWS Access Key ID'
$aws_secret_access_key = Read-Host -Prompt 'AWS Secret Access Key'
$aws_session_token = Read-Host -Prompt 'AWS Session Token'

& aws configure set aws_access_key_id $aws_access_key_id  | Write-Host
& aws configure set aws_secret_access_key $aws_secret_access_key  | Write-Host
& aws configure set aws_session_token $aws_session_token  | Write-Host
& aws configure set default.region us-east-1  | Write-Host
& aws sts get-caller-identity  | Write-Host