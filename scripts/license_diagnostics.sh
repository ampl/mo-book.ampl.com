#!/usr/bin/env bash
# Print what AMPL sees when it fingerprints this machine.
# The ampl binary computes its fingerprint by running hostname, ifconfig
# and ip via popen with PATH=/sbin:/usr/sbin:/bin, while amplkey (used to
# activate) fingerprints natively. Diagnostics only: never fails the job.
set +e
BIN=$(python -c "import ampl_module_base, os; print(os.path.join(os.path.dirname(ampl_module_base.__file__), 'bin'))")
echo "== ampl_module_base bin: $BIN"
echo "== tools visible with AMPL's PATH"
env -i PATH=/sbin:/usr/sbin:/bin sh -c 'for c in hostname ifconfig ip; do printf "%s: " $c; command -v $c || echo MISSING; done'
echo "== hostname"
env -i PATH=/sbin:/usr/sbin:/bin hostname
echo "== ifconfig -a"
env -i PATH=/sbin:/usr/sbin:/bin ifconfig -a
echo "== ip link"
env -i PATH=/sbin:/usr/sbin:/bin ip link
echo "== fingerprint -d -e"
timeout 30 "$BIN/fingerprint" -d -e
echo "== leasefingerprint -d -e"
timeout 30 "$BIN/leasefingerprint" -d -e
echo "== ampl license check"
echo 'option version;' | timeout 30 "$BIN/ampl"
exit 0
