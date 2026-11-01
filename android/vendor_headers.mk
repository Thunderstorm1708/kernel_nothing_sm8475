# SPDX-License-Identifier: GPL-2.0
#
# headers_install for the vendor modules of this kernel (LineageOS inline builds).
#
# The GKI tree only exports its own uapi, but the Qualcomm HALs build against
# the uapi of the SoC drivers and techpacks too. When KCONFIG_EXT_PREFIX points
# at soc-repo, install the uapi directories the modules repo lists in
# build/uapi_headers.mk on top of the kernel's, the way kleaf merges the DDK
# uapi headers into kernel-uapi-headers.tar.gz.

PHONY := __vendor_headers
__vendor_headers:

include $(srctree)/scripts/Kbuild.include

MODULES_REPO := $(patsubst %/,%,$(dir $(patsubst %/,%,$(KCONFIG_EXT_PREFIX))))
include $(srctree)/$(MODULES_REPO)/build/uapi_headers.mk

hdr-inst := -f $(srctree)/scripts/Makefile.headersinst obj

# Each directory gets its own staging dir: Makefile.headersinst removes the
# headers of a subdirectory (linux/...) that are not its own. Then they are
# copied over the kernel's usr/include, in order.
vendor-dirs := $(join $(addsuffix :,$(shell seq $(words $(VENDOR_UAPI_DIRS)))),$(VENDOR_UAPI_DIRS))

__vendor_headers:
	$(foreach e,$(vendor-dirs),$(Q)$(MAKE) $(hdr-inst)=$(MODULES_REPO)/$(word 2,$(subst :, ,$(e))) \
		dst=usr/vendor-uapi/$(word 1,$(subst :, ,$(e)))$(newline))
	$(foreach e,$(vendor-dirs),$(Q)cp -a usr/vendor-uapi/$(word 1,$(subst :, ,$(e)))/. usr/include/$(newline))

.PHONY: $(PHONY)
