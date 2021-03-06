
--アプリについて--
SynthesizerV保存ファイル(.s5p)を各種歌声合成ソフト対応ファイル(予定)に変換するアプリです
オマケ要素として無声化やベロシティの変更などができます(主に歌うボイスロイド向け)
なお、VOCALOID用ファイル(.vpr)についてはKotonoSync以外での利用はできません

--Lite(軽量版)について--
GUIが軽いだけなのでCPUがある程度のスペックがあれば基本は通常版でいいかと思います
ファイル変換以外使わないのであればどちらでも

--バージョンアップについて--
ver.α0.20より解凍時のフォルダ名が[V-Conv]に統一されるようにしました。
旧[V-Conv]フォルダに解凍した同名フォルダを上書きしてsetup.exeを起動すれば設定等全て引き継がれます。
setup.exeに無駄に管理者権限付いてますが名前の都合です。許して。
アプリ名をhoge.exeとか適当に変えれば権限外れます。

--開発環境--
Windows10 pro 64bit
Visual Studio Code ver.1.39.2
Python 3.7.5 64bit

--動作確認環境--
WindowsOS
KotonoSync ver.2.3.8(vprファイル)
CeVIO Creative Studio6 ver.6.1.55.1(ccsファイル)

--使い方--
1. アプリを起動し、変換元ファイルのボタン、またはドラッグアンドドロップでファイルを選択する
2. 変換する

--その他できること--
・メニューバー＞開く/履歴 より以前編集した内容を引き継いでファイルを開くことができます
　保存自体はアプリ終了時にオートセーブがされる仕様になっているのでアプリを閉じずに
　複数ファイルを変換した場合などはバックアップが行われない可能性があります
・設定＞ノート編集＞基本設定 よりノート編集を有効にすると歌詞、発音、ベロシティなどの
　変更ができます
　が、現状クソ重くて多分実用には向かないと思います ごめん
　C#に移植したら改善すると思うのでオマケ程度に忘れるかGitHubよりソースコード落として直接
　使ってください exe化しなければある程度まともに動きます
・設定＞ノート編集＞無声化設定より入力した歌詞に応じて自動で無声化する機能が使えます。
　ただこれKotonoSyncでもできるのでそこまで恩恵はないかもしれません

--設定について--
・保存設定
保存先フォルダ設定：ファイル選択時に保存先フォルダを固定することができます
　　　　　　　　　　オフの場合の初期設定は変換元ファイルと同一ディレクトリになります

・ノート編集
基本設定：ノート編集の有効化/無効化を切り替えます。現状はゴミ機能です
無声化設定：KotonoSync同様ひらがな/カタカナ/その他アルファベット等での無声化を
　　　　　　切り替えることができます
　　　　　　無声化の仕様についてはKotonoSyncの規則に準じています
編集拡張：ベロシティの編集を可能にします。デフォルトの値は64です
　　　　　ベロシティはKotonoSyncにおいて子音の長さに関係するパラメータです

--GitHubについて--
画面中央右あたりにある[Clone or download]よりダウンロード・解凍した上でファイル内にある
.keepファイルを削除し利用してください
なお、利用にあたりPython3(3.7.5以上を推奨)及びwxPythonのインストールが必要になります
その他ツールキットは気分によって使ってるものが変わるので文句言われたら
pipから適当にインストールしてください

--連絡先等--
何かあれば下記twitterに連絡をお願いします

雪花咲里(https://twitter.com/hanayuki7793)
GitHub(https://github.com/Yukikazari/V-Conv)

