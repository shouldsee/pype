mkdir -p build
rm examples -f
ln -sf ../examples/ build/
ln -sf ../pype/ build/
cd build/
rm -rf ./"#"*
#python3 -m pdb -cc -m examples.task_gromacs
python3 -m pdb -cc -m examples.task_ngl
