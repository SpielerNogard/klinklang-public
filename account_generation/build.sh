echo "Building klinklang..."
rm -rf dist
rm -rf pyarmor_runtime_000000
pip install pyarmor
pyarmor gen .
if [ -d "dist" ]; then
    echo "'dist/' directory created."
else
    echo "Failed to create 'dist/' directory."
    exit 1
fi
echo "klinklang build $(date)" > dist/build.txt
if [ -f "dist/build.txt" ]; then
    echo "build.txt created successfully."
else
    echo "Failed to create build.txt in 'dist/'."
    exit 1
fi
cp  -r dist/pyarmor_runtime_000000 pyarmor_runtime_000000
cp dist/account_generator_.py account_generator.py
cp dist/build.txt build.txt
echo "klinklang build complete."

