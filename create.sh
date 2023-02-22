#!/bin/sh

default_files ()
{
 if [ -f accs.mi ]; then
	echo """
==> accs.mi <==
#acc_title;user_key;pass_hint

==> info.mi <==
#acc_title*(str);at_pwsafe(bool);info_str

==> pmap.mi <==
#pass_hint;pass_value

==> rank.mi <==
#acc_title;rank;desc

==> users.mi <==
#user;user_name
	"""
	echo
	echo "Cowardly refusing to initialize."
	return 1
 fi
 echo "#acc_title;user_key;pass_hint" > accs.mi
 echo "#acc_title*(str);at_pwsafe(bool);info_str" > info.mi
 echo "#pass_hint;pass_value" > pmap.mi
 echo "#acc_title;rank;desc" > rank.mi
 echo "#user;user_name" > users.mi
 return $?
}


#
# Main script
#
if [ ! -d $HOME/pdir ]; then
	echo "Creating $HOME/pdir ..."
	mkdir -p $HOME/pdir
fi
CUR=$(pwd)
[ "$CUR" = "" ] && exit 1
cd $HOME/pdir
[ $? != 0 ] && exit 2
default_files
RES=$?

# Run checker
cd $CUR
export PYTHONPATH=$(pwd)/packages
python3 $(pwd)/packages/pword/pcheckersconfig.py
python3 $(pwd)/packages/pword/pcheckers.py


# Exit status
exit $RES
