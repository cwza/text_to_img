data_dir="/root/data/coco"
mkdir -p $data_dir

# # Training images
# curl http://images.cocodataset.org/zips/train2014.zip --output $data_dir/train2014.zip
# 7z x $data_dir/train2014.zip -o$data_dir
# rm -rf $data_dir/train2014.zip

# # Validation images
# curl http://images.cocodataset.org/zips/val2014.zip --output $data_dir/val2014.zip
# 7z x $data_dir/val2014.zip -o$data_dir
# rm -rf $data_dir/val2014.zip

# Annotations
curl http://images.cocodataset.org/annotations/annotations_trainval2014.zip --output $data_dir/annotations_trainval2014.zip
7z x $data_dir/annotations_trainval2014.zip -o$data_dir
rm -rf $data_dir/val2014.zip $data_dir/annotations_trainval2014.zip

