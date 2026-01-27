#if UNITY_2018_3_OR_NEWER

#else
using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

public class Legacy_GUITexture_Updater : ScriptableWizard 
{
	const string kVersion = "1.0";

    [MenuItem("Assets/Upgrade Legacy GUITexture")]
    public static void ShowWindow()
    {
        ScriptableWizard.DisplayWizard<Legacy_GUITexture_Updater>("Upgrade Legacy Particles v" + kVersion, "Upgrade Selected", "Upgrade Everything");
    }

	private GUIText[] guiTexts;

	private GUITexture[] guiTextures;

    void OnWizardUpdate()
    {
        helpString = @"This Script Replace GUIText|GUITexture with MyGUIText|MyGUITexture.
        This script supports Unity versions between 2017.4 and 2018.2.";
    }

    // Find selected assets
    void OnWizardCreate()
    {
        guiTexts = GameObject.FindObjectsOfType<GUIText>();
		guiTextures = GameObject.FindObjectsOfType<GUITexture>();

		UpgradeAll();
    }

    // Find all assets
    void OnWizardOtherButton()
    {
		List<GUIText> text_list = new List<GUIText>();
		List<GUITexture> texture_list = new List<GUITexture>();

		string[] prefabGUIDs = AssetDatabase.FindAssets("t:Prefab");
		for (int i = 0; i < prefabGUIDs.Length; i++)
		{
			GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(AssetDatabase.GUIDToAssetPath(prefabGUIDs[i]));
			GUIText[] texts = prefab.GetComponentsInChildren<GUIText>(true);
			if ( texts != null && texts.Length > 0 ) {
				text_list.AddRange(texts);
			}
			GUITexture[] textures = prefab.GetComponentsInChildren<GUITexture>(true);
			if ( textures != null && textures.Length > 0 ) {
				texture_list.AddRange(textures);
			}
		}

		guiTexts = text_list.ToArray();
		guiTextures = texture_list.ToArray();

		Debug.Log("guiTexts count = " + guiTexts.Length);
		Debug.Log("guiTextures count = " + guiTextures.Length);

		UpgradeAll();

		AssetDatabase.SaveAssets();
    }

	void UpgradeAll()
	{
		Debug.Log("UpgradeAll!");

		try
		{
			for (int i = 0; i < guiTexts.Length; i++) {
				Upgrade( guiTexts[i] );
			}

			for (int i = 0; i < guiTextures.Length; i++) {
				Upgrade( guiTextures[i] );
			}			
		}
        finally
        {
            EditorUtility.ClearProgressBar();
        }


	}

	void Upgrade(GUIText guiText) {
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

	void Upgrade(GUITexture guiTexture) {
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