using UnityEngine;
using UnityEditor;

public class AnimationClipResaver
{
    [MenuItem("Tools/Legacy-Tool/Resave All Animation Clips")]
    public static void ResaveAllAnimationClips()
    {
        // Find all AnimationClip assets in Assets/
        string[] guids = AssetDatabase.FindAssets("t:AnimationClip", new[] { "Assets" });

        if (guids.Length == 0)
        {
            Debug.Log("No AnimationClip assets found in Assets folder.");
            return;
        }

        int count = 0;

        AssetDatabase.StartAssetEditing();
        try
        {
            foreach (string guid in guids)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                AnimationClip clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(path);

                if (clip == null)
                    continue;

                EditorUtility.SetDirty(clip);     // mark as modified
#if UNITY_2019
                AssetDatabase.SaveAssetIfDirty(clip);
#endif

                count++;
            }
        }
        finally
        {
            AssetDatabase.StopAssetEditing();
            AssetDatabase.SaveAssets();
        }

        Debug.Log("Resaved " + count + " AnimationClip assets.");
    }
}
