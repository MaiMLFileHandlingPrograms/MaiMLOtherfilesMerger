let inputCount = 1;

function addInput() {
    inputCount++;
const inputBody = document.getElementById('input-body');
const newRow = document.createElement('tr');
newRow.classList.add('tr-input-group');
    /*newInput.innerHTML = `
            <th scope="row">${inputCount}</th>
            <td><input type="file" name="upload_other" required></td>
            <td>
                <select name="instanceID_list" required>
                    <option value="ID1">ID1</option>
                    <option value="ID2">ID2</option>
                    <option value="ID3">ID3</option>
                </select>
            </td>
            <td><button type="button" onclick="removeInput(this)" class="btn btn-warning">削除</button></td>

        <th scope="row">${inputCount}</th>
        <td>{{ form.upload_other }}</td>
        <td>{{ form.instanceID_list }}</td>
        <td><button type="button" onclick="removeInput(this)" class="btn btn-warning">削除</button></td>
        `;
    */

newRow.innerHTML = `
    <th scope="row">${inputCount}</th>
    <td><input type="file" name="upload_other" required multiple></td>
    <td>${ instanceIDList }</td>
    <td><button type="button" onclick="removeInput(this)" class="btn btn-warning">削除</button></td>
    `;
inputBody.appendChild(newRow);
    updateRowNumbers();
}

function removeInput(button) {
    const row = button.parentElement.parentElement; // ボタンの親の親（行）を取得
    row.remove();
    updateRowNumbers();
}

function updateRowNumbers() {
    const rows = document.querySelectorAll('#input-body .tr-input-group');
    rows.forEach((row, index) => {
    row.querySelector('th').textContent = index + 1; // 行番号を更新
    });
}

document.getElementById('files_update_btn').addEventListener('click', function () {
    const inputBody = document.getElementById('input-body');
    const fileData = [];

    inputBody.querySelectorAll('.tr-input-group').forEach(row => {
        const fileInput = row.querySelector('input[type="file"]');
        const instanceSelect = row.querySelector('select[name="instanceID_list"]');

        if (fileInput.files.length > 0) {
            Array.from(fileInput.files).forEach(file => {
                fileData.push({
                    filename: file.name,
                    instanceID: instanceSelect.value
                });
            });
        }
    });

    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = 'file_data';
    hiddenInput.value = JSON.stringify(fileData);
    document.getElementById('fromidupload').appendChild(hiddenInput);

    document.getElementById('fromidupload').submit();
});

/*
document.getElementById('tiff_update_btn').addEventListener('click', function () {
        const inputBody = document.getElementById('input-body');
const fileData = [];

        // 各行をループし、ファイルとインスタンスIDを取得
        inputBody.querySelectorAll('.tr-input-group').forEach(row => {
            const fileInput = row.querySelector('input[type="file"]');
const instanceSelect = row.querySelector('select[name="instanceID_list"]');

            if (fileInput.files.length > 0) {
    fileData.push({
        filename: fileInput.files[0].name,
        instanceID: instanceSelect.value
    });
            }
        });

// fileDataをJSON形式にして、hiddenフィールドに設定
const hiddenInput = document.createElement('input');
hiddenInput.type = 'hidden';
hiddenInput.name = 'file_data';  // ビューで受け取る名前
hiddenInput.value = JSON.stringify(fileData);
document.getElementById('createdata').appendChild(hiddenInput);

// フォームを送信
document.getElementById('createdata').submit();
    });
*/
/*
    document.getElementById('tiff_update_btn').addEventListener('click', function () {
        const inputBody = document.getElementById('input-body');
const fileData = [];

        inputBody.querySelectorAll('.tr-input-group').forEach(row => {
            const fileInput = row.querySelector('input[type="file"]');
const instanceSelect = row.querySelector('select[name="instanceID_list"]');

// 各ファイルをループ
for (let i = 0; i < fileInput.files.length; i++) {
    fileData.push({
        filename: fileInput.files[i].name,
        instanceID: instanceSelect.value
    });
            }
        });

// fileDataをJSON形式にして、hiddenフィールドに設定
const hiddenInput = document.createElement('input');
hiddenInput.type = 'hidden';
hiddenInput.name = 'file_data';  // ビューで受け取る名前
hiddenInput.value = JSON.stringify(fileData);
document.getElementById('createdata').appendChild(hiddenInput);

// フォームを送信
document.getElementById('createdata').submit();
    });
*/