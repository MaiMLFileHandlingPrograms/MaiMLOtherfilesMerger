from django.db import models
import os

########################
###  master class
########################
## Maiml type
class Maimltype(models.Model):
    model_type = models.IntegerField(verbose_name="Model type", default=0) 
    type_name = models.TextField(verbose_name="Model Name", blank=False)
    # 0:protocolFileRootType/1:maimlRootType
    def __str__(self):
        return str(self.type_name)

#######################################
## util method - create path of files
#######################################
def path_branch(instance, filename):
    root_ext_pair = os.path.splitext(filename)  # ファイルパス＋ファイル名と拡張子を分割
    newfileid = instance.upload_maiml_id
    # input or outputディレクトリ変更
    if root_ext_pair[0].split()[-1] == '.outputdocs':
        dir = f'outputdocs/{newfileid}'
    else:
        dir = f'inputdocs/{newfileid}'
    if root_ext_pair[1] == '.maiml':
        path = os.path.join(dir+'/MaiML/', filename)
    return path

def path_branch2(instance, filename):
    root_ext_pair = os.path.splitext(filename)  # ファイルパス＋ファイル名と拡張子を分割
    newfileid = instance.upload_maiml_id
    # input or outputディレクトリ変更
    if root_ext_pair[0].split()[-1] == '.inputdocs':
        dir = f'inputdocs/{newfileid}'
    else:
        dir = f'outputdocs/{newfileid}'
    path = os.path.join(dir+'/Others/', filename)

    return path

#################################################
##  Model class - save other files 
#################################################
class OtherFiles(models.Model):
    upload_maiml_id = models.UUIDField()
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to = path_branch2, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # temp flag
    commit_flag = models.BooleanField(default=True) 
    class Meta:
        # 複合ユニークキーの指定
        unique_together = ('upload_maiml_id', 'filename')
    document = models.ForeignKey(
        'Document',  # Document モデルを参照
        on_delete=models.deletion.CASCADE,  # Document が削除された場合、関連する OtherFiles も削除
        related_name='other_files',  # 逆参照用の名前
        null=True,  # 外部キーが必須でない場合、null=True を設定
        blank=True   # blank=True は管理画面などで空を許容
    )

#################################################
##  Model class -save maiml and tiff files 
#################################################
class Document(models.Model):
    upload_maiml_id = models.UUIDField(primary_key=True)
    description = models.CharField(max_length=255, blank=True)
    # MaiML File repository PATH
    upload_maiml = models.FileField(upload_to = path_branch)
    # uploaded date
    register_at = models.DateTimeField(auto_now_add=True)
    # temp flag
    commit_flag = models.BooleanField(default=True) 

    # foreign Key
    MaiMLtype = models.ForeignKey(
        Maimltype,
        on_delete=models.PROTECT,
        null=True,
        verbose_name="protocolFileRootType")

    ''' for admin '''
    def __str__(self):
        return str(self.upload_maiml_id)

