# github-actions-prod-deploy-sample

GitHub Actions から AWS Lambda へデプロイする見本です。dev と stg はブランチへのマージで自動、prd だけは Actions の画面から手動で実行します。

| ブランチ | 環境 | デプロイのきっかけ |
|:--|:--|:--|
| develop | dev | push（マージ）で自動 |
| staging | stg | push（マージ）で自動 |
| main | prd | Actions の「Deploy Prd」を main で手動実行 |

「Deploy Prd」では、通常リリース（minor）、修正リリース（patch）、大規模リリース（major）の3つから選ぶと、最新のタグから次の版番号が決まり、リリースノートつきのリリースが作られます。リリースは下書きで作り、デプロイと確かめが成功したときだけ公開します。

## ファイル

| パス | 役割 |
|:--|:--|
| `.github/workflows/_deploy-lambda.yml` | 3つの環境で共通の、ビルドからデプロイまでの手順（呼び出し用のワークフロー） |
| `.github/workflows/deploy-dev.yml`、`deploy-stg.yml` | ブランチへの push で dev、stg へデプロイ |
| `.github/workflows/deploy-prd.yml` | 手動実行で、版番号の決定、下書きのリリース、デプロイ、公開 |
| `.github/workflows/rollback-prd.yml` | 本番のエイリアスを、前のリリースの Lambda の版へ戻す |
| `.github/workflows/ci.yml` | プルリクエストごとのテスト |
| `.github/release.yml` | 自動生成するリリースノートの分類 |
| `scripts/next_version.py` | 最新のタグとリリースの種類から次の版番号を計算 |
| `infra/` | AWS 側（OIDC プロバイダー、環境ごとのロール、Lambda 関数とエイリアス）を作るスクリプト |

## AWS 側の前提

環境ごとに、Lambda 関数とエイリアス、GitHub Actions が OIDC で引き受けるロールを1つずつ作ります。ロールの信頼ポリシーは、その環境の `sub` だけを許可します。GitHub の Environments には、次の値を登録します。

| 種類 | 名前 | 中身 |
|:--|:--|:--|
| 環境のシークレット | `AWS_ROLE_ARN` | その環境のデプロイ用ロールの ARN |
| 環境の変数 | `FUNCTION_NAME` | Lambda 関数の名前 |
| 環境の変数 | `ALIAS_NAME` | エイリアスの名前 |

ロールの ARN にはアカウント ID が入るので、公開リポジトリではシークレットに入れています。
