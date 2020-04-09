TOPDIR=$(dir $(realpath $(firstword $(MAKEFILE_LIST))))

.PHONY: *

diag:
	bash $(TOPDIR)/diagnostics.sh

printdiag:
	cat $(TOPDIR)/diagnostics.sh

impactscondor:
	bash $(TOPDIR)/impacts.sh

limits:
	bash $(TOPDIR)/limit.sh

printlimits:
	cat $(TOPDIR)/limit.sh

plots:
	python $(TOPDIR)/make_plots.py