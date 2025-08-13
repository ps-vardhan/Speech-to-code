public interface AccountRepository extends JpaRepository<Account,Long>{
    Account findByAccountNumber(Long AccountId);
    // Boolean existsByAccountNumber
    List<Account> findBYUserId(Long userId);
}
