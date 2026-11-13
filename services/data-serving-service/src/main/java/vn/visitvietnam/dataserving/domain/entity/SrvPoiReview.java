package vn.visitvietnam.dataserving.domain.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * JPA Entity mapping POI User Reviews table {@code srv_poi_review}.
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "srv_poi_review", schema = "apps")
public class SrvPoiReview {

    @Id
    @Column(name = "review_id", nullable = false)
    private String reviewId;

    @Column(name = "poi_id")
    private String poiId;

    @Column(name = "rating_overall", precision = 4, scale = 2)
    private BigDecimal ratingOverall;

    @Column(name = "rating_count")
    private Long ratingCount;

    @Column(name = "title")
    private String title;

    @Column(name = "review_text")
    private String reviewText;

    @Column(name = "rating", precision = 4, scale = 2)
    private BigDecimal rating;

    @Column(name = "review_date")
    private String reviewDate;

    @Column(name = "author_name")
    private String authorName;

    @Column(name = "source_name")
    private String sourceName;

    @Column(name = "row_hash")
    private String rowHash;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;
}

