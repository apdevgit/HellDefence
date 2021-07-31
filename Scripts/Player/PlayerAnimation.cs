using UnityEngine;

public class PlayerAnimation : MonoBehaviour
{
    private Animator _animator;

    void Awake()
    {
        _animator = GetComponent<Animator>();
    }

    public void SetAnimator(Animator animator)
    {
        _animator = animator;
    }

    public void SetIsMoving(bool status)
    {
        _animator.SetBool("isMoving", status);
    }

    public void SetIsCasting(bool status)
    {
        _animator.SetBool("isCasting", status);
        _animator.ResetTrigger("OnCastCancel");
    }

    public void SetIsDead(bool status)
    {
        _animator.SetBool("isDead", status);
    }

    public void OnCastCancel()
    {
        _animator.SetTrigger("OnCastCancel");
        _animator.SetBool("isCasting", false);
    }

}
