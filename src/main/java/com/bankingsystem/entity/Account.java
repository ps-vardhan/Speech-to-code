import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name="accounts")
public class Account {
    @Id
    @GeneratedValue(strategy=GeneratedValue.IDENTITY)
    private Long accountId;

    @Column(nullable=false)
    private String accountType;

    @Column(nullable=false)
    private double balance;

    @Column(nullable=false,updatable=false)
    private LocalDateTime createdAt;

    @ManyToOne
    @JoinColumn(name="user_id",nullable=false)
    private User user;

    @OneToMany(mappedBy="account",cascade=CascadeType.ALL,orphanRemoval=true)
    private List<Transaction> transactions=new ArrayList<>();
}
