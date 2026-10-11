PKG = decomposition

$(PKG).gfn: $(PKG).inp $(PKG).spec $(PKG)_package_sample.inp $(PKG)_help.md
	gretlcli --makepkg $(PKG).inp


install: $(PKG).gfn
	echo pkg install $(PKG).gfn --local | gretlcli -b -

clean:
	rm -f $(PKG).gfn
