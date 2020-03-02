# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02_data_coco.ipynb (unless otherwise specified).

__all__ = ['get_tiny_lm_dsets', 'get_small_lm_dsets', 'get_tiny_gen_dsets', 'get_small_gen_dsets', 'get_gen_dls']

# Cell
from typing import List
from fastai2.basics import *
from fastai2.text.all import *
from fastai2.vision.all import *
from pycocotools.coco import COCO

# Internal Cell
train_img_path = Path('/root/data/coco/train2014')
train_anno_path = Path('/root/data/coco/annotations/captions_train2014.json')
val_img_path = Path('/root/data/coco/val2014')
val_anno_path = Path('/root/data/coco/annotations/captions_val2014.json')
tiny_img_path = Path('./tiny_data/tiny_imgs')
tiny_anno_path = Path('./tiny_data/captions_tiny.json')

# Internal Cell
def get_captions(coco):
    anns = coco.dataset['annotations']
    captions = [ann['caption'] for ann in anns]
    return captions

# Internal Cell
def get_lm_dsets(captions, pct=1, valid_pct=0.2):
    captions = captions[:int(len(captions)*pct)]
    df = pd.DataFrame({'caption': captions})
    splits = RandomSplitter(seed=42, valid_pct=valid_pct)(df)
    tfms = [attrgetter('text'), Tokenizer.from_df('caption'), Numericalize()]
    dsets = Datasets(df, [tfms], splits=splits, dl_type=LMDataLoader)
    return dsets

# Cell
def get_tiny_lm_dsets(pct=1, valid_pct=0.2):
    coco = COCO(tiny_anno_path)
    captions = get_captions(coco)
    lm_dsets = get_lm_dsets(captions, pct, valid_pct)
    return lm_dsets

def get_small_lm_dsets(pct=1, valid_pct=0.2):
    coco = COCO(val_anno_path)
    captions = get_captions(coco)
    lm_dsets = get_lm_dsets(captions, pct, valid_pct)
    return lm_dsets

# Internal Cell
def get_captions_by_imgid(coco, img_id: int):
    return [ann['caption'] for ann in coco.imgToAnns[img_id]]
def get_imgfilepath_by_imgid(coco, img_id: int, img_path: Path):
    return img_path/coco.imgs[img_id]['file_name']
def imgpath_to_captions(coco, img_path: Path):
    img_ids = coco.getImgIds()
    return [
        [get_imgfilepath_by_imgid(coco, img_id, img_path), get_captions_by_imgid(coco, img_id)]
         for img_id in img_ids
    ]

# Cell
def get_tiny_gen_dsets(vocab: List, pct=1, valid_pct=0.2):
    coco = COCO(tiny_anno_path)
    items = imgpath_to_captions(coco, tiny_img_path)
    items = items[:int(len(items)*pct)]
    splits = RandomSplitter(seed=42, valid_pct=valid_pct)(items)
    tfms = [
        [lambda item: item[1], lambda captions: random.choice(captions), Tokenizer(SpacyTokenizer()), Numericalize(vocab=vocab)],
        [lambda item: item[0], PILImage.create]
    ]
    dsets = Datasets(items, tfms=tfms, splits=splits)
    return dsets

def get_small_gen_dsets(vocab: List, pct=1, valid_pct=0.2):
    coco = COCO(val_anno_path)
    items = imgpath_to_captions(coco, val_img_path)
    items = items[:int(len(items)*pct)]
    splits = RandomSplitter(seed=42, valid_pct=valid_pct)(items)
    tfms = [
        [lambda item: item[1], lambda captions: random.choice(captions), Tokenizer(SpacyTokenizer()), Numericalize(vocab=vocab)],
        [lambda item: item[0], PILImage.create]
    ]
    dsets = Datasets(items, tfms=tfms, splits=splits)
    return dsets

# Cell
def get_gen_dls(dsets, bs, size):
    pad_idx = dsets.o2i['xxpad']
    dls = dsets.dataloaders(
        bs=bs,
        before_batch=[partial(pad_input, pad_idx=pad_idx)],
        after_item=[ToTensor, Resize(size)],
        after_batch=[IntToFloatTensor(), Normalize.from_stats(torch.tensor([0.5,0.5,0.5]), torch.tensor([0.5,0.5,0.5]))]
    )
    return dls

# Internal Cell
def displayable_caption(caption):
    new_cap = []
    for i, w in enumerate(caption.split()):
        i+=1
        if i>11: break
        new_cap.append(w)
        if i%6==0: new_cap.append('\n')
    return ' '.join(new_cap)

# Cell
@typedispatch
def show_batch(x: TensorText, y: TensorImage, samples, ctxs=None, max_n=10, **kwargs):
    n = min(len(samples), max_n)
    ncols = 4
    nrows = math.ceil(n/ncols)
    figsize = (ncols*4, nrows*4)
    if ctxs is None:
        _, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
        ctxs = ax.flatten()
    for i in range(n):
        caption, img = samples[i]
        img.show(ctxs[i])
        ctxs[i].text(0, -1.5, displayable_caption(caption))