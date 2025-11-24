using UnityEngine;

/// <summary>
/// 模拟 Unity 旧版 GUIText 的组件
/// 使用 OnGUI + GUI.Label 实现
/// </summary>
[ExecuteInEditMode]
public class MyGUIText : MonoBehaviour
{
    [Header("显示文字")]
    [TextArea]
    public string text = "Hello World";

    [Header("字体样式")]
    public Font font;
    public int fontSize = 20;
    public Color color = Color.white;
    public FontStyle fontStyle = FontStyle.Normal;

    [Header("Text anchor")]
    public TextAnchor anchor = TextAnchor.UpperLeft;	
    
    [Header("像素偏移 (pixelOffset)")]
    public Vector2 pixelOffset = Vector2.zero;

    [Header("图层深度 (数值越小越靠前)")]
    public int depth = 0;

	GUIStyle style;

	void Start() {
        // 生成 GUIStyle
        this.style = new GUIStyle();
        this.style.font = font;
        this.style.fontSize = fontSize;
        this.style.fontStyle = fontStyle;
        this.style.normal.textColor = color;
        this.style.alignment = anchor;
        this.style.wordWrap = false;
	}

	public void SetFontSize(int size) {
		this.fontSize = size;

		if ( this.style != null ) {
			this.style.fontSize = fontSize;
		}
	}

	public void SetText(string str) {
		this.text = str;
	}

	public void SetMaterialColor(Color color) {
		this.color = color;

		if ( this.style != null ) {
			this.style.normal.textColor = color;
		}
	}

	public void SetPixelOffset(Vector2 offset) {
		this.pixelOffset = offset;
	}

    void OnGUI()
    {
        if (string.IsNullOrEmpty(text)) return;

        // Save GUI state
        int oldDepth = GUI.depth;
        GUI.depth = depth;

        // Build style
        GUIStyle style = new GUIStyle();
        style.font = font;
        style.fontSize = fontSize;
        style.fontStyle = fontStyle;
        style.normal.textColor = color;
        style.wordWrap = false;                 // 单行自适应
        style.alignment = anchor;               // 文本在矩形内的排版（9宫格）

        // Measure text size
        Vector2 size = style.CalcSize(new GUIContent(text));

        // Convert world normalized pos to screen pos
        Vector3 pos = transform.position;
        float screenX = pos.x * Screen.width;
        float screenY = (1f - pos.y) * Screen.height; // invert Y

        // Default rect origin at anchor point
        float x = screenX;
        float y = screenY;

        // Adjust origin based on screen anchor
        switch (anchor)
        {
            case TextAnchor.UpperLeft:
                break;
            case TextAnchor.UpperCenter:
                x -= size.x / 2f;
                break;
            case TextAnchor.UpperRight:
                x -= size.x;
                break;

            case TextAnchor.MiddleLeft:
                y -= size.y / 2f;
                break;
            case TextAnchor.MiddleCenter:
                x -= size.x / 2f;
                y -= size.y / 2f;
                break;
            case TextAnchor.MiddleRight:
                x -= size.x;
                y -= size.y / 2f;
                break;

            case TextAnchor.LowerLeft:
                y -= size.y;
                break;
            case TextAnchor.LowerCenter:
                x -= size.x / 2f;
                y -= size.y;
                break;
            case TextAnchor.LowerRight:
                x -= size.x;
                y -= size.y;
                break;
        }

        // Apply pixel offset
        x += pixelOffset.x;
        y += pixelOffset.y;

        Rect rect = new Rect(x, y, size.x, size.y);

        // Draw
        GUI.Label(rect, text, style);

        // Restore GUI state
        GUI.depth = oldDepth;
    }
}
