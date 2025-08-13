import java.lang.annotation.Inherited;
import java.math.BigDecimal;
import java.time.LocalDate;

@Entity
@Table(name="transactions")
public class Transaction {
    @Id
    @GeneratedValue(Strategy=GeneratedValue.IDENTITY)
    private Long TransactionId;

    @Column(nullable=false)
    private String balance;

    @Column(nullable=false)
    private BigDecimal amount;

    @Column(nullable=false)
    private LocalDateTime date;

    private Long sourseAccountId;
    private Long destinationAccountId;

    @ManyToOne
    @JoinColumn(name="account_id",nullable=false)

    private Account account;
}
