composition:Lock()

local textNode = composition:AddTool("TextPlus")

if textNode then
    textNode.StyledText = "test"
    
    local out = textNode.Output
    local img = out:GetValue(composition.CurrentTime)
    
    if not img then
        img = out:GetWaitValue(composition.CurrentTime)
    end
    
    if img then
        local d = img.DataWindow
        print("成功！領域:" .. d[1] .. ", " .. d[2] .. ", " .. d[3] .. ", " .. d[4])
    else
        print("画像が取得できませんでした。")
    end
else
    print("ノード作成失敗")
end

composition:Unlock()
