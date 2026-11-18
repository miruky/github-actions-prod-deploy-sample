#!/usr/bin/env bash
# 見本の AWS 側を作るスクリプトです。名前はすべて環境変数で渡します。
#   ENV_NAME       : dev、stg、prd のどれか
#   GITHUB_REPO    : OWNER/REPO の形
#   DEPLOY_ROLE    : GitHub Actions が引き受けるデプロイ用ロールの名前
#   DEPLOY_POLICY  : デプロイ用ロールのインラインポリシーの名前
#   EXEC_ROLE      : Lambda の実行ロールの名前（3環境で共通）
#   FUNCTION_NAME  : Lambda 関数の名前
#   ALIAS_NAME     : エイリアスの名前
#   LOG_GROUP      : 関数のログの出力先
set -euo pipefail

: "${ENV_NAME:?}" "${GITHUB_REPO:?}" "${DEPLOY_ROLE:?}" "${DEPLOY_POLICY:?}" "${EXEC_ROLE:?}" \
  "${FUNCTION_NAME:?}" "${ALIAS_NAME:?}" "${LOG_GROUP:?}"
REGION=ap-northeast-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
PROVIDER_ARN="arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
HERE=$(cd "$(dirname "$0")" && pwd)

# GitHub の OIDC プロバイダーはアカウントに1つだけ作ります（2回目以降はそのまま使います）
if ! aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$PROVIDER_ARN" >/dev/null 2>&1; then
  aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --client-id-list sts.amazonaws.com >/dev/null
fi

# 信頼ポリシーは、この環境の sub だけを通します
sub_value=$(python3 "$HERE/sub_claim.py" "$GITHUB_REPO" "$ENV_NAME")
sed -e "s|__PROVIDER_ARN__|${PROVIDER_ARN}|" -e "s|__SUB__|${sub_value}|" \
  "$HERE/trust-policy.json" > /tmp/trust-${ENV_NAME}.json
aws iam create-role --role-name "$DEPLOY_ROLE" \
  --assume-role-policy-document "file:///tmp/trust-${ENV_NAME}.json" \
  --max-session-duration 3600 --query Role.RoleName --output text

FN_ARN="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${FUNCTION_NAME}"
sed -e "s|__FN_ARN__|${FN_ARN}|g" "$HERE/deploy-policy.json" > /tmp/deploy-${ENV_NAME}.json
aws iam put-role-policy --role-name "$DEPLOY_ROLE" --policy-name "$DEPLOY_POLICY" \
  --policy-document "file:///tmp/deploy-${ENV_NAME}.json"

# 実行ロールは3環境で共通なので、なければ作ります
if ! aws iam get-role --role-name "$EXEC_ROLE" >/dev/null 2>&1; then
  aws iam create-role --role-name "$EXEC_ROLE" \
    --assume-role-policy-document "file://$HERE/lambda-trust.json" --query Role.RoleName --output text
  aws iam attach-role-policy --role-name "$EXEC_ROLE" \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
  sleep 10
fi

# 最初の版を作り、エイリアスを向けておきます（以後の更新は GitHub Actions が行います）
aws logs create-log-group --log-group-name "$LOG_GROUP" --region "$REGION"
aws logs put-retention-policy --log-group-name "$LOG_GROUP" --retention-in-days 1 --region "$REGION"
workdir=$(mktemp -d)
cp "$HERE/../src/"*.py "$workdir/"
echo "initial" > "$workdir/VERSION"
(cd "$workdir" && zip -qr function.zip .)
aws lambda create-function --function-name "$FUNCTION_NAME" --region "$REGION" \
  --runtime python3.13 --handler app.handler --architectures arm64 \
  --role "arn:aws:iam::${ACCOUNT_ID}:role/${EXEC_ROLE}" \
  --zip-file "fileb://$workdir/function.zip" \
  --environment "Variables={APP_ENV=${ENV_NAME}}" \
  --logging-config "LogFormat=Text,LogGroup=${LOG_GROUP}" \
  --description "sample for ${ENV_NAME}" --query FunctionName --output text
aws lambda wait function-active-v2 --function-name "$FUNCTION_NAME" --region "$REGION"
ver=$(aws lambda publish-version --function-name "$FUNCTION_NAME" --region "$REGION" \
  --description initial --query Version --output text)
aws lambda create-alias --function-name "$FUNCTION_NAME" --name "$ALIAS_NAME" --region "$REGION" \
  --function-version "$ver" --query Name --output text
