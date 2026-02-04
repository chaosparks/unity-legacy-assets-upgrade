using UnityEngine;
using UnityEditor;
using System.Linq;

public class MaterialResaver
{
    [MenuItem("Tools/Legacy-Tool/Resave All Materials")]
    public static void ResaveAllMaterials()
    {
        // Find all materials in the Assets folder
        string[] guids = AssetDatabase.FindAssets("t:Material", new[] { "Assets" });

        if (guids.Length == 0)
        {
            Debug.Log("No materials found in Assets folder.");
            return;
        }

        int count = 0;

        AssetDatabase.StartAssetEditing();
        try
        {
            foreach (string guid in guids)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                Material mat = AssetDatabase.LoadAssetAtPath<Material>(path);

                if (mat == null)
                    continue;

                EditorUtility.SetDirty(mat);       // mark as modified

#if UNITY_2019
                AssetDatabase.SaveAssetIfDirty(mat);
#endif

                count++;
            }
        }
        finally
        {
            AssetDatabase.StopAssetEditing();
            AssetDatabase.SaveAssets();
        }

        Debug.Log("Resave completed. Total materials updated: " + count);
    }
}
