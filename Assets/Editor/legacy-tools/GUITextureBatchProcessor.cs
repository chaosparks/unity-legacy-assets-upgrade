#if UNITY_2018_3_OR_NEWER
#else
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement; // 用于处理场景
using UnityEngine.SceneManagement; // 用于获取场景信息
using System.Collections.Generic;

public class GUITextureBatchProcessor : EditorWindow
{
    [MenuItem("Tools/批量处理 GUITexture (Add MyGUITexture)")]
    public static void ProcessAll()
    {
        //以此防止误操作，弹出确认框
        if (!EditorUtility.DisplayDialog("警告", 
            "此操作将遍历所有 Prefab 和 Scene，修改后无法撤销。\n请确保在运行前已备份项目！", 
            "开始处理", "取消"))
        {
            return;
        }

        // 1. 处理 Prefabs
        ProcessPrefabs();

        // 2. 处理 Scenes
        ProcessScenes();

        // 3. 结束清理
        AssetDatabase.SaveAssets();
        EditorUtility.ClearProgressBar();
        Debug.Log("处理完成！");
    }

    private static void ProcessPrefabs()
    {
        string[] guids = AssetDatabase.FindAssets("t:Prefab");
        int count = 0;

        foreach (string guid in guids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            
            // 显示进度条
            EditorUtility.DisplayProgressBar("正在处理 Prefabs", path, (float)count / guids.Length);
            count++;

            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null) continue;

            // 获取 Prefab 及其子物体中所有的 GUITexture
            // includeInactive = true 确保隐藏的物体也能被找到
            GUITexture[] guiTextures = prefab.GetComponentsInChildren<GUITexture>(true);

            bool isDirty = false;
            foreach (var gt in guiTextures)
            {
                if (ProcessGameObject_GUITexture(gt, gt.gameObject))
                {
                    isDirty = true;
                }
            }

            GUIText[] guiTexts = prefab.GetComponentsInChildren<GUIText>(true);
            foreach (var gt in guiTexts)
            {
                if (ProcessGameObject_GUIText(gt, gt.gameObject))
                {
                    isDirty = true;
                }
            }            

            // 如果有修改，标记 Prefab 为脏，以便 Unity 保存
            if (isDirty)
            {
                EditorUtility.SetDirty(prefab);
            }
        }
    }

    private static void ProcessScenes()
    {
        // 询问用户是否保存当前打开的场景
        if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
        {
            return;
        }

        string[] guids = AssetDatabase.FindAssets("t:Scene");
        int count = 0;

        foreach (string guid in guids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);

            // 显示进度条
            EditorUtility.DisplayProgressBar("正在处理 Scenes", path, (float)count / guids.Length);
            count++;

            // 打开场景
            Scene scene = EditorSceneManager.OpenScene(path);
            if (!scene.IsValid()) continue;

            bool isSceneDirty = false;

            // 获取场景根物体
            GameObject[] rootObjects = scene.GetRootGameObjects();
            foreach (GameObject root in rootObjects)
            {
                // 遍历根物体及其所有子物体
                GUITexture[] guiTextures = root.GetComponentsInChildren<GUITexture>(true);
                foreach (var gt in guiTextures)
                {
                    if (ProcessGameObject_GUITexture(gt, gt.gameObject))
                    {
                        isSceneDirty = true;
                    }
                }

                GUIText[] guiTexts = root.GetComponentsInChildren<GUIText>(true);
                foreach (var gt in guiTexts)
                {
                    if (ProcessGameObject_GUIText(gt, gt.gameObject))
                    {
                        isSceneDirty = true;
                    }
                }                
            }

            // 如果场景被修改，标记并保存
            if (isSceneDirty)
            {
                EditorSceneManager.MarkSceneDirty(scene);
                EditorSceneManager.SaveScene(scene);
            }
        }
    }

    /// <summary>
    /// 具体添加组件的逻辑
    /// </summary>
    /// <param name="go">目标物体</param>
    /// <returns>是否有修改</returns>
    private static bool ProcessGameObject_GUITexture(GUITexture guiTexture, GameObject go)
    {
        Upgrade(guiTexture);
        return true;
    }

    private static bool ProcessGameObject_GUIText(GUIText guiText, GameObject go)
    {
        Upgrade(guiText);
        return true;
    }    

	static void Upgrade(GUIText guiText) {
		if (guiText == null) return;

		MyGUIText myGUIText = guiText.gameObject.GetComponent<MyGUIText>();
		if (null == myGUIText) {
			myGUIText = guiText.gameObject.AddComponent<MyGUIText>();
		}

		myGUIText.text = guiText.text;
		myGUIText.anchor = guiText.anchor;
		myGUIText.font = guiText.font;
		myGUIText.fontSize = guiText.fontSize;
		myGUIText.fontStyle = guiText.fontStyle;
		myGUIText.pixelOffset = guiText.pixelOffset;
	}

	static void Upgrade(GUITexture guiTexture) {
		if (guiTexture == null) return;

		MyGUITexture myGUITexture = guiTexture.gameObject.GetComponent<MyGUITexture>();
		if (null == myGUITexture) {
			myGUITexture = guiTexture.gameObject.AddComponent<MyGUITexture>();
		}

		myGUITexture.m_Texture = guiTexture.texture;
		myGUITexture.m_PixelInset = guiTexture.pixelInset;
		myGUITexture.m_Color = guiTexture.color;
	}    
}
#endif