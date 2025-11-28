using UnityEngine;
using UnityEditor;
using System.Linq;
using UnityEditor.Animations;

public class AnimaterControllerResaver
{
    [MenuItem("Tools/Resave All AnimatorControllers")]
    public static void ResaveAllAnimatorControllers()
    {
        // Find all AnimatorController assets in Assets/
        string[] guids = AssetDatabase.FindAssets("t:AnimatorController", new[] { "Assets" });

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
                AnimatorController mat = AssetDatabase.LoadAssetAtPath<AnimatorController>(path);

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

        Debug.Log("Resave completed. Total AnimatorControllers updated: " + count);
    }
}
