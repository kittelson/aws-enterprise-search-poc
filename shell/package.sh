# Create zip file for agent handler
base_dir=$(pwd)
source_dir="../agent/lambda/agent-handler"
zip_file_name="agent_deployment_package"
cd $source_dir
zip -r $zip_file_name.zip .

cd $base_dir

echo "Created $zip_file_name.zip from directory $source_dir"