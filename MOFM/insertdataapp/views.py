###################################
##  views class
###################################
import copy, xmltodict
import os, time, shutil, zipfile, json
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages
from django.core.files.uploadedfile import * 
from django.db import transaction

from .models import Document, Maimltype, OtherFiles
from .forms import DocumentForm, DataFileUploadForm, MaimlUpdateForm

from .Utils.namespace import defaultNS
from .Utils.staticClass import staticVal, maimlelement, messagesList
from .Utils.createMaiMLFile import MaimlUtil, ReadWriteMaiML, UpdateMaiML
from .Utils.createPNML import MaimlUtilforPNML



###############################################
##    class for URI  list
##     URL/list/  -->  list.html(file list)
###############################################
class ListDL():
    ## 登録済みのMaiMLファイルのリストを表示
    def displayList(request):
        ## 中途半端なデータを削除
        # Document
        Document.objects.filter(commit_flag=False).delete()
        #OtherFiles
        OtherFiles.objects.filter(commit_flag=False).delete()
        
        # commit_flag=TrueのDocumentリストを取得
        doc_file_list = Document.objects.filter(commit_flag=True)
        # doc_file_list = Document.objects.filter(commit_flag=True).prefetch_related('otherfiles')
        file_list = []
        # 各Documentに対応するOtherFilesを取得してfile_listに追加
        for docfileobj in doc_file_list:
            uuid = docfileobj.upload_maiml_id
            
            # OtherFilesのリストを取得
            other_file_list = OtherFiles.objects.filter(upload_maiml_id=uuid,commit_flag=True)
            
            # file_listに辞書を追加
            file_list.append({
                'uuid': uuid,
                'maimlfile': docfileobj,
                'otherfiles': other_file_list
            })
        return render(request, 'list.html', {'file_list': file_list})
    
    ## ZIP DOWNLOAD
    def download_zip(request, upload_maiml_id):
        document_obj = get_object_or_404(Document, pk=upload_maiml_id)
        other_file_list = OtherFiles.objects.filter(upload_maiml_id=upload_maiml_id,commit_flag=True)

        ## zip URI（ディレクトリ構成）を手に入れる
        ## zipを作ってresponseで返す
        response = HttpResponse(content_type='application/zip')
        file_zip = zipfile.ZipFile(response, 'w')
        
        # ZIPファイルをメモリ上で作成するためにBytesIOを使う
        zip_buffer = io.BytesIO()

        # zipfile.ZipFileを使用して、メモリ内のバッファに書き込み
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # メインのドキュメントファイルを書き込む
            maiml_filename = os.path.basename(document_obj.upload_maiml.name)
            zip_file.writestr(maiml_filename, document_obj.upload_maiml.file.read())

            # その他のファイルを書き込む
            for other_file in other_file_list:
                other_filename = other_file.filename
                zip_file.writestr(other_filename, other_file.file.read())

        # バッファの位置を先頭に戻す
        zip_buffer.seek(0)

        # ZIPファイルをレスポンスとして返す
        response = HttpResponse(zip_buffer.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{maiml_filename}.zip"'
        return response

###############################################
##    class for URI  File Upload
##     URL/upload/  -->  maimlfileupload.html  -->  datafileupload.html
###############################################
class DocumentUpload():
    ### FROM: maimlfileupload.html
    ### POST: "save upload files(MaiML)" to 
    def modelform_upload(request):
        if request.method == 'POST':
            try:
                form = DocumentForm(request.POST, request.FILES)
                if form.is_valid():
                    document_uuid = ''
                    if not request.FILES['upload_maiml'].name.split('.')[-1] == 'maiml':
                        form.errors.update({'':'Please select MaiML file.'})
                        print(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()),'  ',"form.errors:::",form.errors)
                        return render(request, 'maimlfileupload.html', {'form': form})
                    try:
                        # # DB, mediaディレクトリにMaiMLファイルを保存
                        uploaded_maimlfile = request.FILES['upload_maiml']
                        #print('uploaded_maimlfile::::',uploaded_maimlfile)
                        maimlfilename = uploaded_maimlfile.name
                        description = request.POST['description']
                        if isinstance(uploaded_maimlfile, InMemoryUploadedFile):
                            # メモリに収まるサイズのファイルの場合
                            try:
                                file_content = uploaded_maimlfile.read()
                                data_dic = xmltodict.parse(file_content, process_namespaces=True, namespaces=defaultNS.namespaces)
                                document_uuid = data_dic[maimlelement.maiml][maimlelement.document][maimlelement.uuid]
                            except Exception as e:
                                print(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()),f"XMLのパース中にエラーが発生しました: {e}")
                                return render(request, 'maimlfileupload.html', {'form': form})
                        elif isinstance(uploaded_maimlfile, TemporaryUploadedFile):
                            # サイズが大きいファイルの場合
                            try:
                                data_dic = xmltodict.parse(uploaded_maimlfile, process_namespaces=True, namespaces=defaultNS.namespaces)
                                document_uuid = data_dic[maimlelement.maiml][maimlelement.document][maimlelement.uuid]
                            except Exception as e:
                                print(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()),f"XMLのパース中にエラーが発生しました: {e}")
                                return render(request, 'maimlfileupload.html', {'form': form})
                        protocol_type = Maimltype.objects.get(model_type = 0) #protocolFileRootType
                        obj, created = Document.objects.update_or_create(
                            upload_maiml_id = document_uuid,
                            defaults= { 'description' : description, 
                                        'upload_maiml' : uploaded_maimlfile,
                                        'MaiMLtype' : protocol_type}
                            )
                    except Exception as e:
                        messages.add_message(request, messages.ERROR, messagesList.registrationError)
                        #print(e)
                        return render(request, 'maimlfileupload.html', {'form':form})
                    if "goinsertdata" in request.POST: # "insert data files"ボタン押下時
                        url = reverse('insertdataapp:toinsertdata', kwargs={'upload_maiml_id': document_uuid})
                        return HttpResponseRedirect(url)
                        #return render(request, 'updateform.html', {'form': updateform})
                else:
                    print(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()),'  ',"form.errors:::",form.errors)
                    form.protocolmodel = 0
                    return render(request, 'maimlfileupload.html', {'form': form})
            except:
                Document.objects.filter(upload_maiml_id = document_uuid).delete()
                shutil.rmtree(settings.MEDIA_ROOT + f'/inputdocs/{document_uuid}')
                return render(request, '500.html', {'form': form})
        else:
            form = DocumentForm()
            form.protocolmodel = 0
            return render(request, 'maimlfileupload.html', {'form': form})


    ### GET: "save upload maiml DATA file and draw pnml"
    ### POST: "save other files and return updateform.html"
    def upload_datafiles(request, upload_maiml_id=""):
        if request.method == 'POST':
            new_maimluuid = ''
            try:
                form = DataFileUploadForm(request.POST, request.FILES)
                #if form.is_valid():   ## コメントアウト
                
                ## 1. requestからmaimlファイルのUUIDを取得
                upload_maiml_id_data = request.POST.get('upload_maiml_id')

                ## 2. ペトリネット図の座標情報をファイルに保存
                pnml_position_data = request.POST['petri_data']
                #print(pnml_position_data)
                positionfilepath = settings.MEDIA_ROOT +'/pnml/' + upload_maiml_id_data + '.position'
                try:
                    f = open(positionfilepath, 'w', encoding='UTF-8')
                    f.write(pnml_position_data)
                except Exception as e:
                    print(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()),'  ',"Failed to save position data.",e)
                    pass

                ## 3. DocumentオブジェクトをDBから取得しインスタンス化 data
                document_obj = Document.objects.get(upload_maiml_id = upload_maiml_id_data)

                # maimlデータを複製し新たなmaimlデータを作成
                maiml_file_path = document_obj.upload_maiml.path
                readWriteMaiML_class = ReadWriteMaiML()
                maimldict = readWriteMaiML_class.readFile(maiml_file_path) 
                new_maimldict = {}
                ## protocolからdataとevenlLogを作成したDict(UUID4も作成)
                updatemaiml = UpdateMaiML()
                new_maimldict = updatemaiml.createFullMaimlDict(maimldict)
                new_maimluuid = new_maimldict[maimlelement.maiml][maimlelement.document][maimlelement.uuid]

                # 5. requestのhidden inputからファイルとインスタンスIDの対応リストを取得
                file_data_json = request.POST.get('file_data') # file_data_json='[{"filename":"Axoneme-56.008.tif","instanceID":"MaterialTemplate1test_instance"}]'
                # JSONデータをパース
                file_data = json.loads(file_data_json) if file_data_json else []
           
                ## other_fileの名前:データのリストを作る
                try:
                    # # DB, mediaディレクトリにファイルを保存
                    uploaded_files = request.FILES.getlist('upload_other')
                    otherFiles_list = []
                    filenamelist = []
                    for uploaded_file in uploaded_files:
                        if uploaded_file.name in filenamelist:
                            pass
                        else:
                            for file_info in file_data:
                                filename = file_info['filename']
                                instance_id = file_info['instanceID']
                                if filename == uploaded_file.name:
                                    otherFiles_list.extend([{'name':uploaded_file.name, 'filedata':uploaded_file, 'instance_id':instance_id}])
                            filenamelist.append(uploaded_file.name)
                    # 各ファイルをインスタンスにinsertionする
                    for item in otherFiles_list:
                        try:
                            filedata = item['filedata']
                            filedata.seek(0)
                            ## insertion
                            updatemaiml2 = UpdateMaiML()
                            new_maimldict = updatemaiml2.addinsertion(new_maimldict, filedata.read(), item['name'], item['instance_id'])
                            ## TIFFの場合メタデータをマージ
                            name, extension = os.path.splitext(item['name'])
                            if extension in ['.tiff', '.tif']:
                                tiffdatadict = {}
                                try:
                                    filedata.seek(0)
                                    maimlutil = MaimlUtil()
                                    tiffdatadict = maimlutil.readTIFF(old_maimluuid=upload_maiml_id_data, new_maimluuid=new_maimluuid, tif_obj=filedata, tif_name=item['name'])
                                    new_maimldict = updatemaiml2.margeTiffMaimlDict(new_maimldict, tiffdatadict, instanceID=item['instance_id'])
                                except Exception as e:
                                    #print(e)
                                    raise(e)
                            
                            '''    
                            # 8. cifの場合
                            print("aaaa-10")
                            #cifdatalist = []
                            if extension == '.cif':
                                print("cif")
                                ciffilepath = os.path.join(MaimlUtil.get_osfilepath(upload_maiml_id_data,1),item['name']) ## uuid/filename.cif
                                cifdatalist = MaimlUtil.readCif(ciffilepath)
                                for cifdata in cifdatalist:
                                    print(cifdata)
                                    ## merge
                            '''
                        except Exception as e:
                            print(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()),f"外部ファイルのマージ中にエラーが発生しました: {e}")
                            raise e
                    #print('[DEBUG]maimldict of having other file path: ',new_maimldict)
                except Exception as e:
                    messages.add_message(request, messages.ERROR, messagesList.registrationError)
                    print(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()),messagesList.registrationError, e)
                    raise(e)

                # Document を新しいUUID,filepath=/output/で登録
                maiml_file_name = document_obj.upload_maiml.name
                maiml_new_path = settings.MEDIA_ROOT+'/'+MaimlUtil.path_branch(new_maimluuid, maiml_file_name.replace('inputdocs', 'outputdocs'))
                os.makedirs(os.path.dirname(maiml_new_path), exist_ok=True)
                
                ## maimlデータをmaiml_new_pathにファイルとして出力
                WM = ReadWriteMaiML()
                maiml_new_path, setuuid = WM.writecontents(new_maimldict, maiml_new_path) # out_filepath=maiml_new_path ,setuuid=new_maimluuid
                #print(maiml_new_path)
                with transaction.atomic():
                    ## new MaiML fileを(Document model)に登録
                    newdescription = 'system updated file:'+ os.path.basename(maiml_file_name)
                    maiml_new_path = str(maiml_new_path).replace(settings.MEDIA_ROOT+'/', '')
                    protocol_type = Maimltype.objects.get(model_type = 1)
                    Document.objects.create(
                        upload_maiml_id = setuuid,
                        description = newdescription, 
                        upload_maiml = maiml_new_path,
                        MaiMLtype = protocol_type,
                        commit_flag = False,
                        )
                    
                    new_document_obj = Document.objects.get(upload_maiml_id = setuuid)
                    ## 4. other filesをDBとディレクトリ（inputディレクトリ）に保存する　※＊output directoryに変更したい
                    uploaded_files = request.FILES.getlist('upload_other')
                    #document_obj.files.add(uploaded_files) 
                    for uploaded_file in uploaded_files:
                        # ファイルを保存する
                        OtherFiles.objects.create(
                            upload_maiml_id = new_maimluuid,
                            filename = uploaded_file.name,
                            file = uploaded_file,
                            document = new_document_obj,
                            )
                
                # create input form
                initial_values = {
                    'upload_maiml_id':new_maimluuid, 
                    'maiml_dict':json.dumps(new_maimldict, cls=DjangoJSONEncoder),
                    }
                updateform = MaimlUpdateForm(initial_values)
                return render(request, 'updateform.html', {'form': updateform})
            except Exception as e: ## 処理開始時の状態に戻す
                #print(e)
                ##DB削除（該当データが存在する場合には削除し、存在しなければ何もしない）
                Document.objects.filter(upload_maiml_id = new_maimluuid).delete()
                OtherFiles.objects.filter(upload_maiml_id = new_maimluuid).delete()
                shutil.rmtree(settings.MEDIA_ROOT + f'/outputdocs/{new_maimluuid}')
                return render(request, '500.html', {'form': form})

        else: ## 初期表示（from maimlupload)
            # maiml-uuidからペトリネット図用のデータを生成する
            # Read MaiML data
            try:
                if upload_maiml_id:
                    document_obj = Document.objects.get(upload_maiml_id = upload_maiml_id)
                    maiml_file_path = document_obj.upload_maiml.path
                    readWriteMaiML_class = ReadWriteMaiML()
                    maimldict = readWriteMaiML_class.readFile(maiml_file_path)
                    petrinetdata = []
                    pnmldatapath = settings.MEDIA_ROOT +'/pnml/' + upload_maiml_id + '.position'
                    if os.path.isfile(pnmldatapath):
                        f = open(pnmldatapath, 'r', encoding='UTF-8')
                        petrinetdata = eval(f.read())
                        f.close()
                    else:
                        ## maiml_dict --> petrinet graph data
                        maimlUtilforPNML = MaimlUtilforPNML()
                        petrinetdata = maimlUtilforPNML.makepnmlgraphdata(maimldict)
                    #print('petrinetfiledata',petrinetdata)

                    # create instance ID List
                    updatemaiml = UpdateMaiML()
                    instance_list, instance_ID_list = updatemaiml.templatelist(maimldict)
                    default_data = {'upload_maiml_id':upload_maiml_id,
                                    'petri_data':json.dumps(petrinetdata, cls=DjangoJSONEncoder),
                                    'instanceID_data':instance_ID_list,
                                    }
                    form = DataFileUploadForm(default_data, instanceID_data=instance_ID_list)
                    form.errors.clear()
                    return render(request, 'selectinstanceID.html', {'form': form})
                else:
                    print(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()),'  ',"Input-data [upload_maiml_id] is null.")
                    return render(request, '500.html', {'form': form})
            except Exception as e:
                    print(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()),'  ',"Internal error occurred.")
                    return render(request, '500.html', {'form': form})
    


#############################################
##    class for URI  Data Update
##     URL/update/  -->   URL/list
#############################################
class DocumentUpdate():
    def update_maiml(request):
        if request.method == 'POST':
            # requestのformからMaiMLの編集情報を取得する
            form = MaimlUpdateForm(request.POST)
            #print('======update_maiml=============')
            
            if not form.is_valid():
                print('not valid')
                print(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()),'  ',"form.errors:::",form.errors)
                #print(form['maiml_dict'])
                return render(request, 'updateform.html', {'form': form,})
            ## MaiMLファイルを更新
            else:
                ## requestのJSONをDictに変換
                full_data_dict = form.cleaned_data['maiml_dict']
                #print(full_data_dict)
                ## DocumentのUUIDを取得
                maiml_uuid = form.cleaned_data['upload_maiml_id']

                with transaction.atomic():
                    doc_obj = Document.objects.get(upload_maiml_id = maiml_uuid)
    
                    maiml_file_name = doc_obj.upload_maiml.name
                    maiml_file_path = settings.MEDIA_ROOT + '/' + str(doc_obj.upload_maiml)
                    #print(maiml_file_path)
                    WM = ReadWriteMaiML()
                    out_filepath, setuuid = WM.writecontents(full_data_dict, maiml_file_path)
                    
                    doc_obj.commit_flag = True
                    doc_obj.save()

                return redirect('insertdataapp:list')
        else:
            return render(request, 'list.html')
