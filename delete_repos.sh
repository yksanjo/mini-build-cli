#!/bin/bash

# Repositories to delete
REPOS=("yoshiegg" "yo-yo" "kani")

echo "This will delete the following GitHub repositories from your account (yksanjo):"
echo ""
for repo in "${REPOS[@]}"; do
    echo "  - yksanjo/$repo"
done
echo ""
echo "⚠️  WARNING: This action CANNOT be undone!"
echo ""
read -p "Are you sure you want to delete these repositories? Type 'yes' to confirm: " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled. No repositories were deleted."
    exit 0
fi

echo ""
echo "Deleting repositories..."

for repo in "${REPOS[@]}"; do
    echo ""
    echo "Deleting yksanjo/$repo..."
    gh repo delete "yksanjo/$repo" --yes
    if [ $? -eq 0 ]; then
        echo "✅ Successfully deleted yksanjo/$repo"
    else
        echo "❌ Failed to delete yksanjo/$repo"
    fi
done

echo ""
echo "Done!"
