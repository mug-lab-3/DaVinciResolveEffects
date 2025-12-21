!Py3: 
composition.Lock()

textNode = composition.AddTool("TextPlus")

if textNode:
    textNode.StyledText = "test"
    
    out_pin = textNode.Output
    img = out_pin.GetValue(composition.CurrentTime)
    
    if not img:
        img = out_pin.GetWaitValue(composition.CurrentTime)
    
    if img:
        d = img.DataWindow
        try:
            print(f"成功！領域: {d[1]}, {d[2]}, {d[3]}, {d[4]}")
        except KeyError:
            print(f"画像は取得できましたが、DataWindowの形式が特殊です: {d}")
    else:
        print("画像が取得できませんでした。")
else:
    print("ノード作成失敗")

composition.Unlock()
