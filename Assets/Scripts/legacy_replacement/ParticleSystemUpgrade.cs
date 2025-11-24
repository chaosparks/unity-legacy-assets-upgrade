using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public static class ParticleSystemUpgrade 
{
	public static float emissionRate(this ParticleSystem particleSystem)
	{
		return particleSystem.emission.rateOverTime.constant;
	}

	public static float startSpeed(this ParticleSystem particleSystem)
	{
		return particleSystem.main.startSpeed.constant;
	}
}
