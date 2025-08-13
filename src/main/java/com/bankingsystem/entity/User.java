@Entity
@Table(name="users",uniqueConstraints=@UniqueConstraints(columnNames="email"))
public class User {
    @Id
    @GenaratedValue(strategy=GenerationType.IDENTITY)
    private Long userID;

    @Column(nullable=false)
    private String name;

    @Column(nullable=false,unique=true)
    private String email;

    @Column(nullable=false)
    private String passwordHash;

    @Column(nullable=false)
    private String role;

    @OneToMany(mappedBy="user",cascade=CascadeType.ALL,orphanRemoval=true)
    private List<Account> accounts=new ArrayList<>();
}
