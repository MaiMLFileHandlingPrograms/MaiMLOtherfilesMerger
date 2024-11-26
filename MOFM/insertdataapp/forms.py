import os
from django import forms
from .models import Document
from .Utils.createMaiMLFile import MaimlUtil

############################################
##  Form class -   File Upload用
############################################
class DocumentForm(forms.ModelForm):
    protocolmodel = forms.CharField
    class Meta:
        model = Document
        #fields = ('description', 'upload_maiml', 'upload_tiff', )
        fields = ('description', 'upload_maiml', )
        widgets = {
            'description' : forms.TextInput(attrs={'placeholder': 'use for system'}),
            'upload_maiml' : forms.FileInput(),
            }

############################################
##  Form class -   DATA File Upload用
############################################
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# 複数のファイルをアップロードするフィールドクラスを作成
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
    
class DataFileUploadForm(forms.Form):
    upload_maiml_id = forms.UUIDField(required=True, widget=forms.TextInput(attrs={'disabled': 'disabled', }))
    ## petri-net graph data
    #petri_data = forms.JSONField(required=True)
    petri_data = forms.JSONField()
    instanceID_list = forms.ChoiceField(required=False)
    #upload_other = forms.FileField() # <--複数にしたい
    #upload_other = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    #upload_other = forms.FileField(widget=forms.FileInput(attrs={'multiple': True}), required=False)
    upload_other = MultipleFileField(required=False)
    #file_data = forms.JSONField(required=False)  # [{filename:"file name",instanceID:"instance ID"}]


    def save(self,upload_maiml_id_data):
        '''path = MaimlUtil.get_osfilepath(upload_maiml_id_data, 1)
        os.makedirs(path, exist_ok=True)
        
        upload_file = self.files['upload_tiff']
        savepath = os.path.join(path, upload_file.name)
        savefile = open(os.path.join(path, upload_file.name),'wb+')
        for chunk in upload_file.chunks():
            savefile.write(chunk)
        return savepath'''
        path = MaimlUtil.get_osfilepath(upload_maiml_id_data, 1)
        os.makedirs(path, exist_ok=True)

        uploaded_files = self.files.getlist('upload_other')  # 複数ファイルの取得
        saved_paths = []  # 保存したファイルのパスを格納するリスト

        for upload_file in uploaded_files:
            savepath = os.path.join(path, upload_file.name)
            with open(savepath, 'wb+') as savefile:
                for chunk in upload_file.chunks():
                    savefile.write(chunk)
            saved_paths.append(savepath)  # 保存したパスを追加

        return saved_paths  # 複数の保存パスを返す
    
    def clean_upload_other(self):
        files = self.files.getlist('upload_other')
        for upload_file in files:
            if upload_file.size > 10 * 1024 * 1024:  # 10MBの制限
                raise forms.ValidationError("File too large ( > 10MB )")
            #if not upload_file.name.endswith('.tiff'):  # 拡張子のチェック
            #    raise forms.ValidationError("Only .tiff files are allowed.")
        return files

    def __init__(self, *args, **kwargs):
        instanceID_data = kwargs.pop('instanceID_data', [])
        super().__init__(*args, **kwargs)
        
        # プルダウンリストの選択肢を設定
        self.fields['instanceID_list'].choices = [(id, id) for id in instanceID_data]

###############################################
##   Form class -  File Update用
###############################################
class MaimlUpdateForm(forms.Form):
    # 更新するMaiMLファイルのUUID
    upload_maiml_id = forms.UUIDField(required=True, widget=forms.TextInput(
            attrs={ 
                'disabled': 'disabled', 
            }
        ))
    # maimlデータ
    maiml_dict = forms.JSONField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)