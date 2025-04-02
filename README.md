# tasindex

## Database Setup Procedure

- `-bail` オプション: インポート中にエラー（主キー重複、外部キー制約違反など）が発生した場合、すぐに処理を停止します。エラー原因の特定に役立ちます。
- `PRAGMA foreign_keys = ON;` をインポート実行時にも渡すことで、インポート中も外部キー制約がチェックされるようにします（import_data.sql 内にも記述していますが、念のため）。

```bash
# 変数定義 (ファイル名を環境に合わせて変更)
DB_FILE="spacecraft_thermal.db"
SCHEMA_FILE="schema.sql"
IMPORT_FILE="import_data.sql"

# 古いデータベースファイルがあれば削除 (クリーンビルドのため)
echo "Removing old database file if it exists..."
rm -f "$DB_FILE"

# 1. スキーマ作成
echo "Creating database schema..."
sqlite3 "$DB_FILE" < "$SCHEMA_FILE"

# 2. データインポート (外部キー制約を有効にして実行)
echo "Importing data from CSV files..."
sqlite3 -bail "$DB_FILE" "PRAGMA foreign_keys = ON;" < "$IMPORT_FILE"
# -bail オプションはエラーが発生したら即座に停止する

# 3. 完了確認 (任意)
echo "Build finished. Checking row counts..."
sqlite3 "$DB_FILE" "SELECT 'Spacecraft', count(*) FROM Spacecraft UNION ALL SELECT 'Software', count(*) FROM Software UNION ALL SELECT 'ThermalAnalysisEntry', count(*) FROM ThermalAnalysisEntry;"
```