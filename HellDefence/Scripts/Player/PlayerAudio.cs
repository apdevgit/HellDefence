using UnityEngine;

public class PlayerAudio : MonoBehaviour
{
    private AudioSource _playerSoundSource;

    void Awake()
    {
        _playerSoundSource = GetComponent<AudioSource>();
    }

    public void PlaySoundOnPlayer(AudioClip clip)
    {
        _playerSoundSource.PlayOneShot(clip);
    }
    
}
