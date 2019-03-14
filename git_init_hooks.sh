#!/bin/sh

HOOKS_DIR=`git rev-parse --git-dir`/hooks

echo "Installing pre-commit hook..."
#
cat <<EOF >>$HOOKS_DIR/pre-commit
#!/bin/sh

ROOT=`git rev-parse --show-toplevel`

cp -f \$ROOT/lovelace/main.yaml \$ROOT/ui-lovelace.yaml

exit
EOF

echo "Done."
