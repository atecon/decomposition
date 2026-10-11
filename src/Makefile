PKG = decomposition

$(PKG).gfn: $(PKG).inp $(PKG).spec $(PKG)_package_sample.inp $(PKG)_help.md ../README.md
	gretlcli --makepkg $(PKG).inp


# The help text doubles as the repository's README
../README.md: $(PKG)_help.md
	cp $(PKG)_help.md ../README.md


install: $(PKG).gfn
	echo pkg install $(PKG).gfn --local | gretlcli -b -

clean:
	rm -f $(PKG).gfn
