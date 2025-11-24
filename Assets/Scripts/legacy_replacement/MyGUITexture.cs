using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MyGUITexture : MonoBehaviour {

	public Texture m_Texture;

	public Color m_Color = Color.white;

	public Rect m_PixelInset = new Rect(0, 0, 100, 100);

	public bool alphaBlend = true;

    [Header("图层深度 (数值越小越靠前)")]
    public int depth = 0;	

	public ScaleMode scaleMode = ScaleMode.StretchToFill;

	// Use this for initialization
	void Start () {
		
	}
	
	// Update is called once per frame
	void Update () {
		
	}

    void OnGUI()
    {
        if (m_Texture == null) return;

        // 保存原有 GUI 设置
        int oldDepth = GUI.depth;
        Color oldColor = GUI.color;

        GUI.depth = depth;
        GUI.color = m_Color;

        // 将 transform.position 映射到屏幕坐标 (0~1 -> 像素)
        Vector3 pos = transform.position;
        float screenX = pos.x * Screen.width;
        float screenY = (1f - pos.y) * Screen.height; // 注意: GUI Y 轴是向下的

        // 计算最终矩形
        Rect rect = new Rect(
            screenX + m_PixelInset.x,
            screenY + m_PixelInset.y,
            m_PixelInset.width,
            m_PixelInset.height
        );

        // 绘制纹理
        GUI.DrawTexture(rect, m_Texture, scaleMode, alphaBlend);

        // 还原 GUI 设置
        GUI.depth = oldDepth;
        GUI.color = oldColor;
    }
}	
